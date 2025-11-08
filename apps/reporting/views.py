from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Reporte, ConsultaReporte
from .serializers import ReporteSerializer, ConsultaReporteSerializer
from .services import generar_reporte

class ReporteViewSet(ModelViewSet):
    queryset = Reporte.objects.all().order_by('-fecha_generacion')
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]  # lectura para usuarios autenticados

    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy','generar']:
            return [IsAdminUser()]  # solo admin genera/crea/edita/elimina
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='generar')
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
        tipo = request.data.get('tipo_reporte')
        formato = request.data.get('formato', 'CSV')
        parametros = request.data.get('parametros') or {}
        prompt = request.data.get('prompt_texto', '')

        try:
            ruta_rel, descripcion = generar_reporte(tipo, formato=formato, params=parametros)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

        rep = Reporte.objects.create(
            tipo_reporte=tipo,
            formato=formato,
            descripcion=descripcion,
            ruta_archivo=ruta_rel
        )
        consulta = ConsultaReporte.objects.create(
            reporte=rep,
            prompt_texto=prompt,
            parametros=parametros
        )
        data = {
            "reporte": ReporteSerializer(rep).data,
            "consulta": ConsultaReporteSerializer(consulta).data
        }
        return Response(data, status=status.HTTP_201_CREATED)

class ConsultaReporteViewSet(ReadOnlyModelViewSet):
    queryset = ConsultaReporte.objects.select_related('reporte').all().order_by('-fecha_solicitud')
    serializer_class = ConsultaReporteSerializer
    permission_classes = [IsAuthenticated]
