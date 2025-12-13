from rest_framework import serializers
from .models import Bicicleta, Repuesto, Accesorio

class BicicletaSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bicicleta-detail')
    class Meta:
        model = Bicicleta
        fields = '__all__'


class RepuestoSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='repuesto-detail')
    class Meta:
        model = Repuesto
        fields = '__all__'


class AccesorioSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='accesorio-detail')
    class Meta:
        model = Accesorio
        fields = '__all__'
        
