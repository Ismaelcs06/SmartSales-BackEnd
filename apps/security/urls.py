from rest_framework.routers import DefaultRouter
from .views import BitacoraViewSet, DetalleBitacoraViewSet

router = DefaultRouter()
router.register(r'bitacoras', BitacoraViewSet, basename='bitacora')
router.register(r'detalles', DetalleBitacoraViewSet, basename='detalle-bitacora')

urlpatterns = router.urls
