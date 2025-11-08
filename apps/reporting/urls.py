from rest_framework.routers import DefaultRouter
from .views import ReporteViewSet, ConsultaReporteViewSet

router = DefaultRouter()
router.register(r'reportes', ReporteViewSet, basename='reporte')
router.register(r'consultas', ConsultaReporteViewSet, basename='consulta-reporte')

urlpatterns = router.urls
