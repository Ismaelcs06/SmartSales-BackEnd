from rest_framework import serializers
from .models import Bitacora, DetalleBitacora


class DetalleBitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleBitacora
        fields = "__all__"
        # Borra la línea 'read_only_fields = fields'


class BitacoraSerializer(serializers.ModelSerializer):
    detalles = DetalleBitacoraSerializer(many=True, read_only=True)

    class Meta:
        model = Bitacora
        fields = "__all__"
        # Borra la línea 'read_only_fields = fields'
