from django.db import models

class Reporte(models.Model):
    TIPOS = (
        ('ventas', 'Ventas'),
        ('clientes', 'Clientes'),
        ('productos', 'Productos'),
        ('ia', 'IA'),
    )
    FORMATOS = (
        ('CSV', 'CSV'),
        ('JSON', 'JSON'),
        # ('PDF','PDF'),  # si luego implementas PDF
        # ('XLSX','Excel'),  # si luego agregas openpyxl
    )
    tipo_reporte = models.CharField(max_length=30, choices=TIPOS)
    formato = models.CharField(max_length=10, choices=FORMATOS, default='CSV')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)
    ruta_archivo = models.CharField(max_length=255, blank=True)  # ruta relativa dentro de MEDIA_ROOT

    def __str__(self):
        return f"{self.tipo_reporte} ({self.formato}) - {self.fecha_generacion:%Y-%m-%d %H:%M}"

class ConsultaReporte(models.Model):
    reporte = models.ForeignKey(Reporte, null=True, blank=True, on_delete=models.SET_NULL, related_name='consultas')
    prompt_texto = models.TextField(blank=True)         # texto o voz transcrita
    parametros = models.JSONField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consulta {self.id} → {self.reporte_id or 'pendiente'}"
