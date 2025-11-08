from django.utils import timezone
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Promocion, ProductoPromocion, Notificacion
from .serializers import PromocionSerializer, ProductoPromocionSerializer, NotificacionSerializer
from apps.catalog.models import Producto

# ---- Promociones ----
class PromocionViewSet(ModelViewSet):
    queryset = Promocion.objects.all()
    serializer_class = PromocionSerializer
    permission_classes = [IsAdminUser]  # solo admin crea/edita; ajusta según tu necesidad

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='activas')
    def activas(self, request):
        now = timezone.now()
        qs = Promocion.objects.filter(estado='activa', fecha_inicio__lte=now, fecha_fin__gte=now)
        data = self.get_serializer(qs, many=True).data
        return Response(data)

# Relación Producto ↔ Promoción
class ProductoPromocionViewSet(ModelViewSet):
    queryset = ProductoPromocion.objects.select_related('producto','promocion').all()
    serializer_class = ProductoPromocionSerializer
    permission_classes = [IsAdminUser]  # admin gestiona asignaciones

# ---- Notificaciones ----
class NotificacionViewSet(ModelViewSet):
    queryset = Notificacion.objects.select_related('user').all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        # usuario normal ve: sus notificaciones + broadcasts (user=null)
        return Notificacion.objects.filter(user__isnull=True) | Notificacion.objects.filter(user=user)

    @action(detail=True, methods=['post'], url_path='marcar-leida')
    def marcar_leida(self, request, pk=None):
        noti = self.get_object()
        noti.leido = True
        noti.save(update_fields=['leido'])
        return Response(self.get_serializer(noti).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser], url_path='broadcast')
    def broadcast(self, request):
        """Crea una notificación para TODOS (user=None)."""
        s = self.get_serializer(data={
            'user': None,
            'titulo': request.data.get('titulo', ''),
            'mensaje': request.data.get('mensaje', ''),
            'tipo': request.data.get('tipo', 'promocion'),
        })
        s.is_valid(raise_exception=True)
        noti = Notificacion.objects.create(
            user=None,
            titulo=s.validated_data['titulo'],
            mensaje=s.validated_data['mensaje'],
            tipo=s.validated_data.get('tipo','promocion')
        )
        return Response(self.get_serializer(noti).data, status=status.HTTP_201_CREATED)
