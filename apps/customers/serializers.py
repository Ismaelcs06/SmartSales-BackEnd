from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    nombre_completo = serializers.CharField(source='user.full_name', read_only=True) 

    class Meta:
        model = Cliente
        fields = [
            'id', 'user', 'username', 'email', 'nombre_completo', 
            'ci_nit', 'telefono', 'direccion', 'ciudad', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro', 'user'] 