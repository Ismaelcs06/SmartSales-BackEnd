from rest_framework import serializers
from .models import Reporte, ConsultaReporte,ModeloEntrenado, PrediccionVenta


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = "__all__"
        read_only_fields = ["id", "fecha_generacion", "ruta_archivo"]


class ConsultaReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultaReporte
        fields = "__all__"
        read_only_fields = ["id", "fecha_solicitud"]


class ModeloEntrenadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeloEntrenado
        fields = "__all__"
        read_only_fields = ["id", "fecha_entrenamiento"]


class PrediccionVentaSerializer(serializers.ModelSerializer):
    # Opcional: añadir info del producto para el dashboard
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = PrediccionVenta
        fields = [
            "id",
            "modelo",
            "producto",
            "producto_nombre",
            "fecha_prediccion",
            "ventas_estimadas",
            "periodo",
            "generado_en",
        ]
        read_only_fields = ["id", "generado_en", "producto_nombre"]
