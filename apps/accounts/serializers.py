from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from apps.customers.models import Cliente 
from django.contrib.auth.models import Group,Permission

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    ci_nit = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)
    direccion = serializers.CharField(write_only=True, required=False, allow_blank=True)
    ciudad = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 
            'nombre', 'apellido_paterno', 'apellido_materno',
            'ci_nit', 'telefono', 'direccion', 'ciudad' 
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Las contraseñas no coinciden."})
        
        try:
            validate_password(data['password'], user=User(**data))
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'password': validated_data['password'],
            'nombre': validated_data.get('nombre', ''),
            'apellido_paterno': validated_data.get('apellido_paterno', ''),
            'apellido_materno': validated_data.get('apellido_materno', ''),
        }
        
        cliente_data = {
            'ci_nit': validated_data.get('ci_nit', ''),
            'telefono': validated_data.get('telefono', ''),
            'direccion': validated_data.get('direccion', ''),
            'ciudad': validated_data.get('ciudad', ''),
        }
        user = User.objects.create_user(**user_data)
        Cliente.objects.filter(user=user).update(**cliente_data)
        return user
    
    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']
        read_only_fields = fields

    

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer para el CRUD de Roles (Grupos).
    Permite ver y asignar permisos al crear/actualizar un rol.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        source='permissions',
        label="IDs de Permisos"
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permission_ids']

    

class UserAdminSerializer(serializers.ModelSerializer):
    """
    Serializer para que el Administrador gestione usuarios (CRUD).
    """
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        label="Roles (Grupos)"
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nombre', 
            'apellido_paterno', 'apellido_materno',
            'is_active', 'is_staff', 'is_superuser', 
            'groups' 
        ]
        read_only_fields = ['id']