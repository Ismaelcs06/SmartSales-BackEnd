from rest_framework import serializers
from .models import Reporte, ConsultaReporte

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = '__all__'
        read_only_fields = ['id','fecha_generacion','ruta_archivo']

class ConsultaReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultaReporte
        fields = '__all__'
        read_only_fields = ['id','fecha_solicitud']
