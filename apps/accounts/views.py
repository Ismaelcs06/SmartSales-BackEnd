
from django.contrib.auth.models import Group, Permission


from rest_framework import generics, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


from .models import User  
from .serializers import (
    UserRegistrationSerializer,
    UserAdminSerializer,
    RoleSerializer,
    PermissionSerializer,
)



class UserRegistrationView(generics.CreateAPIView):
    """
    Vista de API para que nuevos usuarios se registren.
    No requiere autenticación (permiso AllowAny).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Permite a cualquiera registrarse



class UserAdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint para el CRUD de Usuarios (Admin).
    """

    queryset = User.objects.all().prefetch_related("groups").order_by("id")
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]  # <-- SOLO ADMINS

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "email", "nombre", "apellido_paterno"]
    filterset_fields = ["groups", "is_active", "is_staff", "is_superuser"]
    
    


    
class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint para el CRUD de Roles (Grupos) (Admin).
    """

    queryset = Group.objects.all().prefetch_related("permissions").order_by("name")
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]  # <-- SOLO ADMINS
    search_fields = ["name"]

    @action(detail=False, methods=["get"])
    def all_permissions(self, request):
        """
        Endpoint extra para listar todos los permisos disponibles.
        """
        permissions = Permission.objects.all().order_by(
            "content_type__app_label", "codename"
        )
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
