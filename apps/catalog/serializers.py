from rest_framework import serializers
from .models import Categoria, Producto, Garantia

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ['id']


class GarantiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garantia
        fields = '__all__'
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer mejorado para Producto.
    """
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    garantias = GarantiaSerializer(many=True, read_only=True)
    
    # --- ¡CAMBIO IMPORTANTE! ---
    # SerializerMethodField nos da control total sobre la URL
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'marca', 'modelo', 'precio', 'stock',
            'imagen', # <-- Este es el campo para SUBIR
            'imagen_url', # <-- Este es el campo para LEER (la URL completa)
            'estado', 'fecha_registro', 'categoria', 'categoria_nombre', 'garantias' 
        ]
        read_only_fields = ['id', 'fecha_registro', 'imagen_url']
        # Hacemos 'imagen' de solo escritura (write_only) en la lista,
        # pero opcional (required=False) para que no sea obligatorio subir una imagen
        extra_kwargs = {
            'imagen': {'write_only': True, 'required': False}
        }

    def get_imagen_url(self, obj):
        """
        Construye la URL completa de la imagen para el frontend.
        """
        request = self.context.get('request')
        if obj.imagen and hasattr(obj.imagen, 'url'):
            # build_absolute_uri crea la URL completa 
            # (ej: http://127.0.0.1:8000/media/productos/mi-foto.jpg)
            return request.build_absolute_uri(obj.imagen.url)
        return None # Devuelve null si no hay imagen