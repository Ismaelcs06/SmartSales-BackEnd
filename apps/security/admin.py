from django.contrib import admin
from .models import Bitacora, DetalleBitacora

class DetalleInline(admin.TabularInline):
    model = DetalleBitacora
    extra = 0
    readonly_fields = ('accion','fecha','method','path','status_code','detalle','payload','model_label','object_id')

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('id','user','ip','dispositivo','login_at','logout_at','session_key')
    list_filter = ('dispositivo',)
    search_fields = ('user__username','user__email','session_key','ip','user_agent')
    readonly_fields = ('user','session_key','ip','user_agent','dispositivo','login_at','logout_at')
    inlines = [DetalleInline]

@admin.register(DetalleBitacora)
class DetalleBitacoraAdmin(admin.ModelAdmin):
    list_display = ('id','bitacora','accion','fecha','method','path','status_code')
    list_filter = ('accion','status_code','method')
    search_fields = ('path','detalle','model_label','object_id')
    readonly_fields = ('bitacora','accion','fecha','method','path','status_code','detalle','payload','model_label','object_id')
