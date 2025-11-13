from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Categoria, Producto, Garantia
from .serializers import CategoriaSerializer, ProductoSerializer, GarantiaSerializer
from .recommendation import ProductRecommender

# -----------------------------
# VISTAS DE CATEGORÍAS
# -----------------------------
class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.prefetch_related('productos').all().order_by('nombre')
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['nombre']

# -----------------------------
# VISTAS DE PRODUCTOS
# -----------------------------
class ProductoViewSet(ModelViewSet):
    queryset = Producto.objects.select_related('categoria') \
                               .prefetch_related('garantias') \
                               .all().order_by('-id')
    serializer_class = ProductoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria', 'estado', 'marca']
    search_fields = ['nombre', 'descripcion', 'marca', 'modelo']

    # --- Permisos según acción ---
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'recomendados', 'recomendados_usuario']:
            # Usuarios logueados pueden ver lista, detalle y recomendaciones
            self.permission_classes = [IsAuthenticated]
        else:
            # Solo admins pueden crear/actualizar/borrar
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    # --- Filtrado de queryset ---
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(estado='activo')

# --- ENDPOINT PERSONALIZADO: productos recomendados globales para usuario ---
@action(detail=False, methods=['get'], url_path='recomendados-usuario')
def recomendados_usuario(self, request):
    recommender = ProductRecommender()
    
    recommended_ids = set()
    
    # Tomamos algunos productos para calcular recomendaciones
    productos = Producto.objects.filter(estado='activo')[:20]
    
    for producto in productos:
        similar_ids = recommender.get_similar(producto.id, n=3)
        recommended_ids.update(similar_ids)
        if len(recommended_ids) >= 12:
            break
    
    # fallback: si no hay suficientes, completamos con productos activos
    if len(recommended_ids) < 12:
        active_ids = Producto.objects.filter(estado='activo').values_list('id', flat=True)
        recommended_ids.update(active_ids)
    
    # Solo los primeros 12
    recommended_ids = list(recommended_ids)[:12]
    similares = Producto.objects.filter(id__in=recommended_ids)
    
    serializer = self.get_serializer(similares, many=True, context={'request': request})
    return Response(serializer.data)


# -----------------------------
# VISTAS DE GARANTÍAS
# -----------------------------
class GarantiaViewSet(ModelViewSet):
    queryset = Garantia.objects.select_related('producto').all()
    serializer_class = GarantiaSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['producto', 'tipo_garantia', 'estado']
