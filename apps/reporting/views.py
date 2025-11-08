# --- Imports de Python ---
import joblib

# --- Imports de Third-Party (Django, DRF, Pandas) ---
import pandas as pd
from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


from apps.catalog.models import Producto
from .models import (
    Reporte, 
    ConsultaReporte, 
    ModeloEntrenado, 
    PrediccionVenta
)
from .serializers import (
    ReporteSerializer, 
    ConsultaReporteSerializer, 
    ModeloEntrenadoSerializer, 
    PrediccionVentaSerializer
)
from .services import generar_reporte

class ReporteViewSet(ModelViewSet):
    queryset = Reporte.objects.all().order_by("-fecha_generacion")
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated] 

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "generar"]:
            return [IsAdminUser()]  # solo admin genera/crea/edita/elimina
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="generar")
    def generar(self, request):
        """
        body:
        {
          "tipo_reporte": "ventas",
          "formato": "CSV",     // o "JSON"
          "parametros": { "date_from": "2025-10-01", "date_to": "2025-10-31" },
          "prompt_texto": "Ventas de octubre"
        }
        """
        tipo = request.data.get("tipo_reporte")
        formato = request.data.get("formato", "CSV")
        parametros = request.data.get("parametros") or {}
        prompt = request.data.get("prompt_texto", "")

        try:
            ruta_rel, descripcion = generar_reporte(
                tipo, formato=formato, params=parametros
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        rep = Reporte.objects.create(
            tipo_reporte=tipo,
            formato=formato,
            descripcion=descripcion,
            ruta_archivo=ruta_rel,
        )
        consulta = ConsultaReporte.objects.create(
            reporte=rep, prompt_texto=prompt, parametros=parametros
        )
        data = {
            "reporte": ReporteSerializer(rep).data,
            "consulta": ConsultaReporteSerializer(consulta).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class ConsultaReporteViewSet(ReadOnlyModelViewSet):
    queryset = (
        ConsultaReporte.objects.select_related("reporte")
        .all()
        .order_by("-fecha_solicitud")
    )
    serializer_class = ConsultaReporteSerializer
    permission_classes = [IsAuthenticated]


class PrediccionViewSet(ReadOnlyModelViewSet):
    """
    API para ver las predicciones de ventas (para el Dashboard).
    Solo accesible por Admins.
    """

    queryset = PrediccionVenta.objects.all().select_related("producto", "modelo")
    serializer_class = PrediccionVentaSerializer
    permission_classes = [IsAdminUser]  # Solo Admins ven esto
    filterset_fields = ["producto", "periodo", "modelo"]

    @action(detail=False, methods=["get"], url_path="modelos-activos")
    def modelos_activos(self, request):
        """Muestra los modelos que están entrenados y listos para usar."""
        modelos = ModeloEntrenado.objects.all().order_by("-fecha_entrenamiento")
        return Response(ModeloEntrenadoSerializer(modelos, many=True).data)

    @action(detail=False, methods=["post"], url_path="ejecutar-prediccion")
    def ejecutar_prediccion(self, request):
        """
        Ejecuta una nueva predicción (ej. para el próximo mes)
        usando el último modelo entrenado.

        Body (ejemplo):
        {
            "anio": 2025,
            "mes": 12
        }
        """
        try:
            modelo_entrenado = ModeloEntrenado.objects.latest("fecha_entrenamiento")
            model = joblib.load(modelo_entrenado.ruta_archivo)
        except (ModeloEntrenado.DoesNotExist, FileNotFoundError):
            return Response(
                {
                    "detail": "No hay un modelo entrenado. Ejecute 'train_model' primero."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Crear datos de entrada
        anio = request.data.get("anio", timezone.now().year)
        mes = request.data.get("mes", timezone.now().month)

        productos = Producto.objects.filter(estado="activo")
        if not productos.exists():
            return Response(
                {"detail": "No hay productos activos para predecir."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        X_pred = pd.DataFrame(
            {
                "anio": [anio] * len(productos),
                "mes": [mes] * len(productos),
                "producto_id": [p.id for p in productos],
            }
        )

        # 2. Ejecutar Predicción
        predicciones = model.predict(X_pred)

        # 3. Guardar resultados en la BD
        resultados_guardados = []
        fecha_pred = f"{anio}-{mes:02d}-01"

        # Borrar predicciones viejas para este mismo mes/año para no duplicar
        PrediccionVenta.objects.filter(fecha_prediccion=fecha_pred).delete()

        for prod, pred_val in zip(productos, predicciones):
            pred = PrediccionVenta.objects.create(
                modelo=modelo_entrenado,
                producto=prod,
                fecha_prediccion=fecha_pred,
                ventas_estimadas=pred_val if pred_val > 0 else 0,
                periodo="Mensual",
            )
            resultados_guardados.append(pred)

        serializer = PrediccionVentaSerializer(resultados_guardados, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
