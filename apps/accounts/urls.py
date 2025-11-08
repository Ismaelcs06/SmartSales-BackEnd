from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, 
    UserAdminViewSet,  
    RoleViewSet        
)

# 1. Crear un router para los ViewSets de Admin

router = DefaultRouter()
router.register(r'users', UserAdminViewSet, basename='user-admin')
router.register(r'roles', RoleViewSet, basename='role-admin')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('', include(router.urls)),
]