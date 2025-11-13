from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser # <-- ¡IsAdminUser es necesario!
from .models import Bitacora, DetalleBitacora
from .serializers import BitacoraSerializer, DetalleBitacoraSerializer
from django_filters.rest_framework import DjangoFilterBackend # <-- 1. Importar
from rest_framework import filters # <-- 2. Importar

class BitacoraViewSet(ReadOnlyModelViewSet):
    queryset = Bitacora.objects.select_related('user').prefetch_related('detalles').all()
    serializer_class = BitacoraSerializer
    permission_classes = [IsAdminUser] # <-- 3. Solo Admins pueden ver la bitácora
    
    # --- 4. AÑADIR FILTROS Y BÚSQUEDA ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'dispositivo'] # Filtro por usuario o dispositivo
    search_fields = ['ip', 'user_agent', 'user__username', 'session_key'] # Búsqueda

    def get_queryset(self):
        # El admin ve todo, un usuario normal (si quisiéramos) vería lo suyo
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset.order_by('-login_at')
        return self.queryset.filter(user=user).order_by('-login_at')

class DetalleBitacoraViewSet(ReadOnlyModelViewSet):
    queryset = DetalleBitacora.objects.select_related('bitacora','bitacora__user').all()
    serializer_class = DetalleBitacoraSerializer
    permission_classes = [IsAdminUser] # <-- 5. Solo Admins
    
    # --- 6. AÑADIR FILTRO POR BITÁCORA ---
    # Esto es CRÍTICO para ver los detalles de UNA sesión
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bitacora'] # <-- ¡EL MÁS IMPORTANTE!

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset.order_by('-fecha')
        return self.queryset.filter(bitacora__user=user).order_by('-fecha')