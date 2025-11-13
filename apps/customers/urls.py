from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

router = DefaultRouter()
# --- ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
# Añadimos basename='cliente' para ayudar al router
router.register(r'clientes', ClienteViewSet, basename='cliente')

urlpatterns = router.urls