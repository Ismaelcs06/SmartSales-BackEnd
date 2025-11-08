from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'nombre', 'apellido_paterno', 'apellido_materno', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'nombre', 'apellido_paterno', 'apellido_materno')
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información Personal", {
            "fields": ("nombre", "apellido_paterno", "apellido_materno", "email")
        }),
        
        ("Permisos", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Fechas Importantes", {"fields": ("last_login", "date_joined")}),
    )