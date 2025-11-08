# apps/catalog/serializers.py

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
    
    # --- MEJORA 1: Mostrar el nombre de la categoría ---
    # Esto es de SOLO LECTURA, para que el frontend vea el nombre.
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    # --- MEJORA 2: Anidar las garantías del producto ---
    # Esto es de SOLO LECTURA. Muestra la lista de garantías.
    garantias = GarantiaSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'marca', 'modelo', 'precio', 'stock',
            'imagen_url', 'estado', 'fecha_registro',
            
            # --- Campos para ESCRITURA (el ID) ---
            'categoria', 
            
            # --- Campos MEJORADOS (para LECTURA) ---
            'categoria_nombre',
            'garantias' 
        ]
        # Hacemos los campos de auditoría de solo lectura
        read_only_fields = ['id', 'fecha_registro']