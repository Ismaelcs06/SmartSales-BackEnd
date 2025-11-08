from django.db import models
from django.conf import settings 
from apps.catalog.models import Producto 


class Reporte(models.Model):
    TIPOS = (
        ("ventas", "Ventas"),
        ("clientes", "Clientes"),
        ("productos", "Productos"),
        ("ia", "IA"),
    )
    FORMATOS = (
        ("CSV", "CSV"),
        ("JSON", "JSON"),
        # ('PDF','PDF'),  # si luego implementas PDF
        # ('XLSX','Excel'),  # si luego agregas openpyxl
    )
    tipo_reporte = models.CharField(max_length=30, choices=TIPOS)
    formato = models.CharField(max_length=10, choices=FORMATOS, default="CSV")
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)
    ruta_archivo = models.CharField(
        max_length=255, blank=True
    )  # ruta relativa dentro de MEDIA_ROOT

    def __str__(self):
        return f"{self.tipo_reporte} ({self.formato}) - {self.fecha_generacion:%Y-%m-%d %H:%M}"


class ConsultaReporte(models.Model):
    reporte = models.ForeignKey(
        Reporte,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="consultas",
    )
    prompt_texto = models.TextField(blank=True)  # texto o voz transcrita
    parametros = models.JSONField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consulta {self.id} → {self.reporte_id or 'pendiente'}"


class ModeloEntrenado(models.Model):
    """
    Almacena metadatos sobre un modelo de ML (Random Forest)
    que ha sido entrenado y guardado en un archivo (.joblib).
    """

    nombre_modelo = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    ruta_archivo = models.CharField(
        max_length=255
    )  # ej: 'ml_models/sales_rf_v1.joblib'
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True)
    dataset_usado = models.CharField(max_length=255, blank=True)
    precision_modelo = models.FloatField(null=True, blank=True)  # ej: R-squared

    def __str__(self):
        return f"{self.nombre_modelo} (v{self.version})"


class PrediccionVenta(models.Model):
    """
    Almacena el *resultado* de una predicción hecha por un modelo.
    Esto es lo que consumirá el Dashboard.
    """

    modelo = models.ForeignKey(ModeloEntrenado, on_delete=models.SET_NULL, null=True)
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_prediccion = models.DateField()  # ej: 2025-12-01 (para el mes de Dic)
    ventas_estimadas = models.DecimalField(max_digits=12, decimal_places=2)
    periodo = models.CharField(max_length=20)  # ej: 'Mensual'
    generado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_prediccion"]

    def __str__(self):
        return f"Predicción para {self.fecha_prediccion}: {self.ventas_estimadas}"
