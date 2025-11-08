from django.db import models

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    def __str__(self): return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    marca = models.CharField(max_length=80, blank=True)
    modelo = models.CharField(max_length=80, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    imagen_url = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=20, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.nombre

class Garantia(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='garantias')
    duracion_meses = models.IntegerField()
    descripcion_condiciones = models.TextField(blank=True)
    proveedor_servicio = models.CharField(max_length=100, blank=True)
    tipo_garantia = models.CharField(max_length=50)  # fabrica / extendida
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='activa')
