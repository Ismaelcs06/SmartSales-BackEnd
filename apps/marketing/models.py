from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.catalog.models import Producto

class Promocion(models.Model):
    ESTADOS = (('activa', 'Activa'), ('inactiva', 'Inactiva'))
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)  # 0–100
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activa')
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.titulo} ({self.descuento_porcentaje}%)"

    @property
    def activa_ahora(self):
        now = timezone.now()
        return self.estado == 'activa' and self.fecha_inicio <= now <= self.fecha_fin


class ProductoPromocion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='promociones_rel')
    promocion = models.ForeignKey(Promocion, on_delete=models.CASCADE, related_name='productos_rel')

    class Meta:
        unique_together = ('producto', 'promocion')

    def __str__(self):
        return f"{self.producto} ↔ {self.promocion}"


class Notificacion(models.Model):
    TIPOS = (('alerta','Alerta'), ('promocion','Promoción'), ('recordatorio','Recordatorio'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=120)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='alerta')
    leido = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    # Si es broadcast, user = null

    class Meta:
        ordering = ['-fecha_envio']

    def __str__(self):
        to = self.user.username if self.user else "Todos"
        return f"[{self.tipo}] {self.titulo} → {to}"
