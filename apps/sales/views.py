from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers

from .models import Venta, DetalleVenta, Factura, Pago
from apps.catalog.models import Producto

# Intentar importar serializers desde apps/sales/serializers.py, si no existen creamos fallbacks seguros
try:
    from .serializers import VentaSerializer, FacturaSerializer, PagoSerializer, DetalleVentaSerializer
except Exception:
    # Fallback mínimo para evitar ImportError en runtime. Recomendado: crear serializers reales en apps/sales/serializers.py
    class DetalleVentaSerializer(drf_serializers.ModelSerializer):
        class Meta:
            model = DetalleVenta
            fields = '__all__'

    class VentaSerializer(drf_serializers.ModelSerializer):
        detalles = DetalleVentaSerializer(many=True, read_only=True)
        class Meta:
            model = Venta
            fields = '__all__'

    class FacturaSerializer(drf_serializers.ModelSerializer):
        class Meta:
            model = Factura
            fields = '__all__'

    class PagoSerializer(drf_serializers.ModelSerializer):
        class Meta:
            model = Pago
            fields = '__all__'


class VentaViewSet(ModelViewSet):
    """
    ModelViewSet para Ventas. create():
    - valida existencia y stock de productos
    - crea la Venta y los DetalleVenta
    - actualiza stock (select_for_update)
    - crea factura asociada (simple)
    """
    queryset = Venta.objects.all().order_by('-fecha_venta')
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        items = data.get('items') or []
        cliente_id = data.get('cliente')
        metodo_pago = data.get('metodo_pago', 'tarjeta')

        if not cliente_id:
            return Response({"detail": "cliente es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        if not items:
            return Response({"detail": "items es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = Decimal('0.00')
        detalles_info = []

        for it in items:
            prod_id = it.get('producto')
            if prod_id is None:
                return Response({"detail": "Cada item debe contener 'producto'."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                prod = Producto.objects.select_for_update().get(pk=prod_id)
            except Producto.DoesNotExist:
                return Response({"detail": f"Producto {prod_id} no encontrado."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                qty = int(it.get('cantidad', 1))
                if qty <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return Response({"detail": f"cantidad inválida para producto {prod_id}."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                precio_unitario = Decimal(str(it.get('precio_unitario', prod.precio)))
                if precio_unitario < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError, TypeError):
                return Response({"detail": f"precio_unitario inválido para producto {prod_id}."}, status=status.HTTP_400_BAD_REQUEST)

            if hasattr(prod, 'stock') and prod.stock is not None and prod.stock < qty:
                return Response({"detail": f"Stock insuficiente para producto {prod.id}."}, status=status.HTTP_400_BAD_REQUEST)

            total_line = precio_unitario * qty
            subtotal += total_line
            detalles_info.append({
                'producto': prod,
                'cantidad': qty,
                'precio_unitario': precio_unitario,
                'total_line': total_line,
            })

        venta = Venta.objects.create(
            cliente_id=cliente_id,
            fecha_venta=timezone.now(),
            metodo_pago=metodo_pago,
            total=subtotal,
            estado_venta='completada'
        )

        for info in detalles_info:
            DetalleVenta.objects.create(
                venta=venta,
                producto=info['producto'],
                cantidad=info['cantidad'],
                precio_unitario=info['precio_unitario'],
                total=info['total_line']
            )
            prod = info['producto']
            if hasattr(prod, 'stock') and prod.stock is not None:
                prod.stock = max(0, prod.stock - info['cantidad'])
                prod.save(update_fields=['stock'])

        numero = f"F-{timezone.now().strftime('%Y%m%d')}-{venta.pk}"
        Factura.objects.create(
            venta=venta,
            numero_factura=numero,
            fecha_emision=timezone.now(),
            subtotal=subtotal,
            descuento=Decimal('0.00'),
            total=subtotal,
            metodo_pago=venta.metodo_pago,
            estado='emitida'
        )

        serializer = VentaSerializer(venta, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FacturaViewSet(ModelViewSet):
    """
    ViewSet para Facturas.
    """
    queryset = Factura.objects.all().order_by('-fecha_emision')
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated]


class PagoViewSet(ModelViewSet):
    """
    ViewSet para Pagos.
    """
    queryset = Pago.objects.all().order_by('-fecha_pago')
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]