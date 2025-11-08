from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nombre = models.CharField(max_length=100, blank=True)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)

    def full_name(self):
        base = self.nombre or self.first_name
        ap = self.apellido_paterno or ''
        am = self.apellido_materno or ''
        return " ".join(x for x in [base, ap, am] if x).strip()

    def __str__(self):
        return self.username or self.email or self.full_name()

