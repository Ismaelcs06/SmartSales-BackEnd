from rest_framework.routers import DefaultRouter
from .views import CarritoViewSet

router = DefaultRouter()
router.register(r'carritos', CarritoViewSet, basename='carrito')

urlpatterns = router.urls
