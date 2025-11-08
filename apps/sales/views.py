from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.customers.models import Cliente
from apps.cart.models import Carrito, DetalleCarrito
from apps.catalog.models import Producto
from .models import Venta, DetalleVenta, Pago, Factura
from .serializers import VentaSerializer, FacturaSerializer, PagoSerializer

class VentaViewSet(ReadOnlyModelViewSet):
    """Listado y detalle de ventas del usuario. Acciones: checkout."""
    permission_classes = [IsAuthenticated]
    serializer_class = VentaSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Venta.objects.select_related('cliente').prefetch_related('detalles__producto')
        if user.is_staff or user.is_superuser:
            return qs.order_by('-id')
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Venta.objects.none()
        return qs.filter(cliente=cliente).order_by('-id')

    @action(detail=False, methods=['post'], url_path='checkout')
    @transaction.atomic
    def checkout(self, request):
        """
        Espera:
        {
          "metodo_pago": "tarjeta",
          "descuento": "0.00",
          "referencia_transaccion": "opcional"
        }
        """
        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)

        try:
            carrito = Carrito.objects.select_for_update().get(cliente=cliente, estado='activo')
        except Carrito.DoesNotExist:
            return Response({"detail": "No hay carrito activo."}, status=400)

        detalles = list(DetalleCarrito.objects.select_for_update().filter(carrito=carrito).select_related('producto'))
        if not detalles:
            return Response({"detail": "El carrito está vacío."}, status=400)

        # Validar stock
        for d in detalles:
            if d.producto.stock < d.cantidad:
                return Response({"detail": f"Stock insuficiente para {d.producto.nombre}."}, status=400)

        # Calcular totales
        subtotal = sum((d.cantidad * d.precio_unitario for d in detalles), Decimal('0.00'))
        descuento = Decimal(request.data.get('descuento', '0.00'))
        total = subtotal - descuento
        if total < 0:
            total = Decimal('0.00')

        metodo_pago = request.data.get('metodo_pago', 'tarjeta')
        referencia = request.data.get('referencia_transaccion', '')

        # Crear venta
        venta = Venta.objects.create(
            cliente=cliente,
            fecha_venta=timezone.now(),
            metodo_pago=metodo_pago,
            total=total,
            estado_venta='completada'  # asumimos pago ok (puedes cambiar flujo)
        )

        # Crear detalles y descontar stock
        for d in detalles:
            DetalleVenta.objects.create(
                venta=venta,
                producto=d.producto,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                total=d.cantidad * d.precio_unitario
            )
            # descontar stock
            p = d.producto
            p.stock -= d.cantidad
            p.save(update_fields=['stock'])

        # Pago
        pago = Pago.objects.create(
            venta=venta,
            metodo=metodo_pago,
            monto=total,
            estado_pago='exitoso',  # si integras pasarela, cámbialo según respuesta
            referencia_transaccion=referencia
        )

        # Factura (numero simple; en prod usarías tu generador)
        numero = f"F-{venta.pk:06d}"
        factura = Factura.objects.create(
            venta=venta,
            numero_factura=numero,
            subtotal=subtotal,
            descuento=descuento,
            total=total,
            metodo_pago=metodo_pago,
            estado='emitida'
        )

        # Cerrar carrito y limpiar detalles
        carrito.estado = 'cerrado'
        carrito.save(update_fields=['estado'])
        carrito.detalles.all().delete()

        data = {
            "venta": VentaSerializer(venta).data,
            "pago": PagoSerializer(pago).data,
            "factura": FacturaSerializer(factura).data
        }
        return Response(data, status=status.HTTP_201_CREATED)
