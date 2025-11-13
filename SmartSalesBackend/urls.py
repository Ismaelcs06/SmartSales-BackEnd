"""
URL configuration for SmartSalesBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Esquema OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Autenticación JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Aquí montaremos rutas de tus apps, p. ej.:
    # Conecta las URLs de 'accounts' (como el registro)
    path('api/auth/', include('apps.accounts.urls')),
    # path('api/catalog/', include('apps.catalog.urls')),
    
    path('api/catalog/',include('apps.catalog.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/marketing/', include('apps.marketing.urls')),
    path('api/security/', include('apps.security.urls')),
    path('api/reporting/', include('apps.reporting.urls')),
]


# --- ¡AÑADIR ESTO AL FINAL! ---
# Esto le dice a Django que sirva los archivos de la carpeta MEDIA_ROOT
# cuando DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
