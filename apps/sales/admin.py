from django.contrib import admin
from .models import Venta, DetalleVenta, Pago, Factura

class DetalleInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','fecha_venta','metodo_pago','total','estado_venta')
    list_filter = ('estado_venta','metodo_pago')
    inlines = [DetalleInline]

admin.site.register(DetalleVenta)
admin.site.register(Pago)
admin.site.register(Factura)
