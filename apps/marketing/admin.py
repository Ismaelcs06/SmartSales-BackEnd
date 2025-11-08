from django.contrib import admin
from .models import Promocion, ProductoPromocion, Notificacion

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('id','titulo','descuento_porcentaje','fecha_inicio','fecha_fin','estado')
    list_filter = ('estado',)
    search_fields = ('titulo','descripcion')

@admin.register(ProductoPromocion)
class ProductoPromocionAdmin(admin.ModelAdmin):
    list_display = ('id','producto','promocion')
    search_fields = ('producto__nombre','promocion__titulo')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id','titulo','tipo','user','leido','fecha_envio')
    list_filter = ('tipo','leido')
    search_fields = ('titulo','mensaje','user__username','user__email')
