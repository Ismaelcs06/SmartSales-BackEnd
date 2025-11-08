from rest_framework import serializers
from .models import Promocion, ProductoPromocion, Notificacion
from apps.catalog.models import Producto

class PromocionSerializer(serializers.ModelSerializer):
    activa_ahora = serializers.BooleanField(read_only=True)
    class Meta:
        model = Promocion
        fields = ['id','titulo','descripcion','descuento_porcentaje','fecha_inicio','fecha_fin','estado','activa_ahora','creada_en']
        read_only_fields = ['id','activa_ahora','creada_en']

class ProductoPromocionSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    promocion_titulo = serializers.CharField(source='promocion.titulo', read_only=True)
    class Meta:
        model = ProductoPromocion
        fields = ['id','producto','producto_nombre','promocion','promocion_titulo']
        read_only_fields = ['id','producto_nombre','promocion_titulo']

class NotificacionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Notificacion
        fields = ['id','user','username','titulo','mensaje','tipo','leido','fecha_envio']
        read_only_fields = ['id','username','fecha_envio']
