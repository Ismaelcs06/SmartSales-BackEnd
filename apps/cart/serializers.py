from rest_framework import serializers
from .models import Carrito, DetalleCarrito
from apps.catalog.models import Producto

class DetalleCarritoSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = DetalleCarrito
        fields = ['id', 'producto', 'nombre_producto', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['id', 'nombre_producto', 'subtotal']

class CarritoSerializer(serializers.ModelSerializer):
    detalles = DetalleCarritoSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'cliente', 'estado', 'fecha_creacion', 'actualizado_en', 'detalles', 'total']
        read_only_fields = ['id', 'fecha_creacion', 'actualizado_en', 'detalles', 'total']

class AddItemSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)

    def validate(self, data):
        try:
            producto = Producto.objects.get(pk=data['producto_id'])
        except Producto.DoesNotExist:
            raise serializers.ValidationError("Producto no existe.")
        if producto.estado != 'activo':
            raise serializers.ValidationError("Producto no disponible.")
        if producto.stock < data['cantidad']:
            raise serializers.ValidationError("Stock insuficiente.")
        data['producto'] = producto
        return data
