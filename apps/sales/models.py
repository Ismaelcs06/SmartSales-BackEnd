from django.db import models
from django.utils import timezone
from django.conf import settings

from apps.customers.models import Cliente
from apps.catalog.models import Producto

class Venta(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    fecha_venta = models.DateTimeField(default=timezone.now)
    metodo_pago = models.CharField(max_length=30, default='tarjeta')  # tarjeta, efectivo, stripe, etc.
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado_venta = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Venta #{self.pk} - {self.cliente}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

class Pago(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
    )
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='pago')
    metodo = models.CharField(max_length=30)  # tarjeta, stripe, etc.
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(default=timezone.now)
    estado_pago = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    referencia_transaccion = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Pago {self.estado_pago} - Venta #{self.venta_id}"

class Factura(models.Model):
    ESTADOS = (
        ('emitida', 'Emitida'),
        ('anulada', 'Anulada'),
        ('pendiente', 'Pendiente'),
    )
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='factura')
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=30)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='emitida')
    observaciones = models.TextField(blank=True)
    ruta_pdf = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Factura {self.numero_factura}"
