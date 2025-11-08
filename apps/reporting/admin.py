from django.contrib import admin
from .models import Reporte, ConsultaReporte

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id','tipo_reporte','formato','fecha_generacion','ruta_archivo')
    list_filter = ('tipo_reporte','formato')
    search_fields = ('descripcion','ruta_archivo')

@admin.register(ConsultaReporte)
class ConsultaReporteAdmin(admin.ModelAdmin):
    list_display = ('id','reporte','fecha_solicitud')
    search_fields = ('prompt_texto',)
