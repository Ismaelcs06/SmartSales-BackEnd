from django.conf import settings
from django.db import models
from django.utils import timezone

# Usaremos Cliente (perfil 1:1 con User)
from apps.customers.models import Cliente
from apps.catalog.models import Producto

class Carrito(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('cerrado', 'Cerrado'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='carritos')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        # una regla de negocio útil: 1 carrito activo por cliente
        constraints = [
            models.UniqueConstraint(
                fields=['cliente'], condition=models.Q(estado='activo'),
                name='uniq_carrito_activo_por_cliente'
            )
        ]

    def __str__(self):
        return f"Carrito #{self.pk} - {self.cliente} ({self.estado})"

    @property
    def total(self):
        return sum(d.subtotal for d in self.detalles.all())


class DetalleCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='en_carritos')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot del precio

    class Meta:
        unique_together = ('carrito', 'producto')  # un renglón por producto

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
