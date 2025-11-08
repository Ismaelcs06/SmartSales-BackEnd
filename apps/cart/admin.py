from django.contrib import admin
from .models import Carrito, DetalleCarrito

class DetalleInline(admin.TabularInline):
    model = DetalleCarrito
    extra = 0

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','estado','fecha_creacion','actualizado_en','total')
    list_filter = ('estado',)
    inlines = [DetalleInline]

@admin.register(DetalleCarrito)
class DetalleCarritoAdmin(admin.ModelAdmin):
    list_display = ('id','carrito','producto','cantidad','precio_unitario')
