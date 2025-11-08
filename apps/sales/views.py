# apps/sales/views.py

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

# --- Imports de Rest Framework ---
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

# --- Imports de otras Apps ---
from apps.cart.models import Carrito, DetalleCarrito
from apps.catalog.models import Producto
from apps.customers.models import Cliente

# --- Imports Locales (esta app) ---
from .models import Venta, DetalleVenta, Pago, Factura
from .serializers import VentaSerializer, FacturaSerializer, PagoSerializer

# -----------------------------------------------------------------

class VentaViewSet(ReadOnlyModelViewSet):
    """
    Listado y detalle de ventas.
    Admins ven todo, usuarios ven solo sus ventas.
    Incluye la acción de 'checkout'.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VentaSerializer

    def get_queryset(self):
        """
        Optimizado para incluir cliente, usuario, pago, factura y detalles
        en el menor número de consultas.
        """
        user = self.request.user
        
        # --- MEJORA DE OPTIMIZACIÓN APLICADA ---
        # Añadimos 'cliente__user', 'pago', y 'factura' al select_related
        qs = Venta.objects.select_related(
            'cliente', 'cliente__user', 'pago', 'factura'
        ).prefetch_related(
            'detalles__producto'
        )

        if user.is_staff or user.is_superuser:
            return qs.order_by('-id')
        try:
            # Asumimos que un usuario no-staff es un cliente
            cliente = user.cliente
        except Cliente.DoesNotExist:
            # Si el usuario no es staff y no tiene perfil de cliente, no ve nada
            return Venta.objects.none()
            
        return qs.filter(cliente=cliente).order_by('-id')

    @action(detail=False, methods=['post'], url_path='checkout')
    @transaction.atomic
    def checkout(self, request):
        """
        Crea una Venta, Pago y Factura a partir del carrito activo del cliente.
        Valida el stock y descuenta las unidades.
        Limpia el carrito al finalizar.

        Espera:
        {
          "metodo_pago": "tarjeta",
          "descuento": "0.00",
          "referencia_transaccion": "opcional"
        }
        """
        # --- (Tu lógica de checkout es excelente y se mantiene intacta) ---
        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            carrito = Carrito.objects.select_for_update().get(cliente=cliente, estado='activo')
        except Carrito.DoesNotExist:
            return Response({"detail": "No hay carrito activo."}, status=status.HTTP_400_BAD_REQUEST)

        detalles = list(DetalleCarrito.objects.select_for_update().filter(carrito=carrito).select_related('producto'))
        if not detalles:
            return Response({"detail": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar stock
        for d in detalles:
            if d.producto.stock < d.cantidad:
                return Response({"detail": f"Stock insuficiente para {d.producto.nombre}."}, status=status.HTTP_400_BAD_REQUEST)

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
            estado_venta='completada'
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
            estado_pago='exitoso',
            referencia_transaccion=referencia
        )

        # Factura
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


# --- VISTAS ADICIONALES (READ-ONLY) AÑADIDAS ---

class PagoViewSet(ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura para Pagos.
    Admins ven todo, usuarios ven solo sus pagos.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PagoSerializer
    
    def get_queryset(self):
        user = self.request.user
        qs = Pago.objects.select_related('venta', 'venta__cliente__user')
        if user.is_staff:
            return qs.order_by('-id')
        
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Pago.objects.none()
            
        return qs.filter(venta__cliente=cliente).order_by('-id')

class FacturaViewSet(ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura para Facturas.
    Admins ven todo, usuarios ven solo sus facturas.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FacturaSerializer
    
    def get_queryset(self):
        user = self.request.user
        qs = Factura.objects.select_related('venta', 'venta__cliente__user')
        if user.is_staff:
            return qs.order_by('-id')

        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Factura.objects.none()

        return qs.filter(venta__cliente=cliente).order_by('-id')