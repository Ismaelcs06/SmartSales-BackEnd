from rest_framework.routers import DefaultRouter
from .views import PromocionViewSet, ProductoPromocionViewSet, NotificacionViewSet

router = DefaultRouter()
router.register(r'promociones', PromocionViewSet, basename='promocion')
router.register(r'producto-promocion', ProductoPromocionViewSet, basename='producto-promocion')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = router.urls
