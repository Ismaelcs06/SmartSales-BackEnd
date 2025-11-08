from django.db import models
from django.conf import settings

# Create your models here.

class Cliente(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cliente'
    )
    ci_nit = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=150, blank=True)
    ciudad = models.CharField(max_length=50, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre = getattr(self.user, "full_name", lambda: "")()
        return nombre or self.user.username or self.user.email

