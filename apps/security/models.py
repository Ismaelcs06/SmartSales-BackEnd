from django.conf import settings
from django.db import models
from django.utils import timezone

class Bitacora(models.Model):
    """Sesión del usuario (login → logout)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='bitacoras')
    session_key = models.CharField(max_length=40, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    dispositivo = models.CharField(max_length=80, blank=True)
    login_at = models.DateTimeField(default=timezone.now)
    logout_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-login_at']

    def __str__(self):
        u = self.user.username if self.user else "anon"
        return f"Bitácora {self.pk} ({u})"

class DetalleBitacora(models.Model):
    """Evento dentro de una sesión: request, modelo creado, etc."""
    ACCIONES = (
        ('request', 'Request'),
        ('login_failed', 'Login fallido'),
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('other', 'Otro'),
    )
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='detalles')
    accion = models.CharField(max_length=20, choices=ACCIONES, default='request')
    fecha = models.DateTimeField(auto_now_add=True)

    # Datos HTTP
    method = models.CharField(max_length=10, blank=True)
    path = models.CharField(max_length=512, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    # Snapshot/payload
    detalle = models.TextField(blank=True)
    payload = models.JSONField(null=True, blank=True)

    # Cambios en modelos (opcional)
    model_label = models.CharField(max_length=120, blank=True)  # "app.Model"
    object_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.accion} {self.method} {self.path} ({self.status_code})"
