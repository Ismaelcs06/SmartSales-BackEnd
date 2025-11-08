from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ci_nit', 'telefono', 'ciudad', 'fecha_registro')
    search_fields = ('user__username', 'user__email', 'ci_nit', 'telefono', 'ciudad')
    list_filter = ('ciudad',)
