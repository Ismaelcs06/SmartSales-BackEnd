from rest_framework.routers import DefaultRouter
from .views import ReporteViewSet, ConsultaReporteViewSet
from .views import PrediccionViewSet

router = DefaultRouter()
router.register(r'reportes', ReporteViewSet, basename='reporte')
router.register(r'consultas', ConsultaReporteViewSet, basename='consulta-reporte')
router.register(r'predicciones', PrediccionViewSet, basename='prediccion')

urlpatterns = router.urls