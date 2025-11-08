from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, PagoViewSet, FacturaViewSet # <-- Importa las nuevas

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'pagos', PagoViewSet, basename='pago')       # <-- AÑADE ESTA
router.register(r'facturas', FacturaViewSet, basename='factura') # <-- AÑADE ESTA

urlpatterns = router.urls