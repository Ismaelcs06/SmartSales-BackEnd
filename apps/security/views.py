from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Bitacora, DetalleBitacora
from .serializers import BitacoraSerializer, DetalleBitacoraSerializer

class BitacoraViewSet(ReadOnlyModelViewSet):
    queryset = Bitacora.objects.select_related('user').prefetch_related('detalles').all()
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_staff or u.is_superuser:
            return qs
        return qs.filter(user=u)

class DetalleBitacoraViewSet(ReadOnlyModelViewSet):
    queryset = DetalleBitacora.objects.select_related('bitacora','bitacora__user').all()
    serializer_class = DetalleBitacoraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_staff or u.is_superuser:
            return qs
        return qs.filter(bitacora__user=u)
