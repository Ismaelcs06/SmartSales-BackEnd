from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ProductoViewSet, GarantiaViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'productos',  ProductoViewSet)
router.register(r'garantias',  GarantiaViewSet)

urlpatterns = router.urls
