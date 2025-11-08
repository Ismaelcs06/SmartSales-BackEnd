from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from .models import Carrito, DetalleCarrito
from .serializers import CarritoSerializer, DetalleCarritoSerializer, AddItemSerializer
from apps.customers.models import Cliente

class CarritoViewSet(ModelViewSet):
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Carrito.objects.select_related('cliente__user').prefetch_related('detalles__producto')
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return qs.order_by('-id')  # admin ve todos
        # cliente normal: solo sus carritos
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Carrito.objects.none()
        return qs.filter(cliente=cliente).order_by('-id')

    @action(detail=False, methods=['get'], url_path='mi-activo')
    def mi_activo(self, request):
        """Devuelve (o crea) el carrito activo del usuario actual."""
        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)

        carrito, _ = Carrito.objects.get_or_create(cliente=cliente, estado='activo')
        data = CarritoSerializer(carrito).data
        return Response(data)

    @action(detail=False, methods=['post'], url_path='add-item')
    @transaction.atomic
    def add_item(self, request):
        """Agrega o incrementa un producto en el carrito activo del usuario."""
        s = AddItemSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        producto = s.validated_data['producto']
        cantidad = s.validated_data['cantidad']

        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)

        carrito, _ = Carrito.objects.get_or_create(cliente=cliente, estado='activo')

        detalle, created = DetalleCarrito.objects.select_for_update().get_or_create(
            carrito=carrito, producto=producto,
            defaults={'cantidad': 0, 'precio_unitario': producto.precio}
        )
        # actualizar cantidad y snapshot de precio (por si cambió)
        detalle.cantidad += cantidad
        detalle.precio_unitario = producto.precio
        detalle.save()

        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='remove-item')
    @transaction.atomic
    def remove_item(self, request):
        """Decrementa o elimina un producto del carrito activo."""
        s = AddItemSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        producto = s.validated_data['producto']
        cantidad = s.validated_data['cantidad']

        user = request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            return Response({"detail": "Este usuario no tiene perfil de cliente."}, status=400)

        try:
            carrito = Carrito.objects.get(cliente=cliente, estado='activo')
            detalle = DetalleCarrito.objects.select_for_update().get(carrito=carrito, producto=producto)
        except (Carrito.DoesNotExist, DetalleCarrito.DoesNotExist):
            return Response({"detail": "El producto no está en el carrito."}, status=400)

        nueva = detalle.cantidad - cantidad
        if nueva <= 0:
            detalle.delete()
        else:
            detalle.cantidad = nueva
            detalle.save()

        return Response(CarritoSerializer(carrito).data)

    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        """Vacía el carrito activo del usuario."""
        user = request.user
        try:
            cliente = user.cliente
            carrito = Carrito.objects.get(cliente=cliente, estado='activo')
        except (Cliente.DoesNotExist, Carrito.DoesNotExist):
            return Response({"detail": "No hay carrito activo."}, status=400)
        carrito.detalles.all().delete()
        return Response(CarritoSerializer(carrito).data)
