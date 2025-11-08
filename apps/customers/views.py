from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.select_related('user').all().order_by('id')
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ciudad', 'ci_nit', 'user']

    # limitar que un usuario "cliente" solo vea/edite su perfil.
    # Descomentar para activar esa restricción:
    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     user = self.request.user
    #     if user.is_superuser or user.is_staff:
    #         return qs
    #     return qs.filter(user=user)
