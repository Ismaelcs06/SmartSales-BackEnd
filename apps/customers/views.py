from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser # <-- 1. Importa IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(ModelViewSet):
    """
    CRUD para perfiles de Clientes.
    - Admins: Ven una lista de SOLO clientes (no otros admins).
    - Clientes: Solo pueden ver/editar su PROPIO perfil.
    """
    serializer_class = ClienteSerializer
    # 2. Permiso más estricto: solo Admins pueden ver la LISTA
    permission_classes = [IsAdminUser] 
    filter_backends = [DjangoFilterBackend]
    # 3. Añadimos 'user__username' y 'user__email' a los filtros
    filterset_fields = ['ciudad', 'ci_nit', 'user__username', 'user__email']
    search_fields = ['ci_nit', 'telefono', 'ciudad', 'user__username', 'user__email', 'user__nombre']

    def get_queryset(self):
        # 4. Optimizamos la consulta para incluir el 'user'
        qs = Cliente.objects.select_related('user')
        
        user = self.request.user

        if user.is_staff:
            # 5. ¡LA SOLUCIÓN!
            # Si el que mira es Admin, le mostramos todos los clientes,
            # PERO excluimos a los que también son 'staff'.
            return qs.filter(user__is_staff=False).order_by('id')
        
        # 6. Si un cliente (no-staff) intenta usar este endpoint,
        # solo se verá a sí mismo (esto es una medida de seguridad).
        return qs.filter(user=user).order_by('id')

    def get_permissions(self):
        """
        Sobrecarga de permisos:
        - Admins (is_staff) pueden hacer todo (CRUD).
        - Clientes (no-staff) solo pueden ver (GET) o editar (PUT/PATCH)
          su propio perfil (si acceden a /api/customers/clientes/1/)
        """
        if self.action in ['list', 'create', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]