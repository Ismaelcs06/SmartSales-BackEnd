from rest_framework import serializers
from .models import Venta, DetalleVenta, Pago, Factura

# --- Serializers de Pago y Factura (ya los tenías, están perfectos) ---
class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id','venta','metodo','monto','fecha_pago','estado_pago','referencia_transaccion']
        read_only_fields = ['id','fecha_pago']

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = ['id','venta','numero_factura','fecha_emision','subtotal','descuento','total',
                  'metodo_pago','estado','observaciones','ruta_pdf']
        read_only_fields = ['id','fecha_emision']

# --- Serializer de Detalle (ya lo tenías, está perfecto) ---
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    class Meta:
        model = DetalleVenta
        fields = ['id','producto','producto_nombre','cantidad','precio_unitario','total']
        read_only_fields = ['id','producto_nombre','total', 'producto', 'precio_unitario', 'cantidad']

# --- MEJORA EN VentaSerializer ---
class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    
    # --- ¡MEJORA! Anidamos el pago y la factura ---
    pago = PagoSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.user.full_name', read_only=True) # Bonus

    class Meta:
        model = Venta
        fields = [
            'id','cliente', 'cliente_nombre', 'fecha_venta','metodo_pago',
            'total','estado_venta',
            'detalles', # Lista de productos
            'pago',     # Objeto de pago
            'factura'   # Objeto de factura
        ]
        read_only_fields = ['id','fecha_venta','total','estado_venta','detalles', 'pago', 'factura', 'cliente_nombre']