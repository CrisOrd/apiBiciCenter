from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Bicicleta, Repuesto, Accesorio
from .serializers import BicicletaSerializer, RepuestoSerializer, AccesorioSerializer

class BicicletaViewSet(viewsets.ModelViewSet):
    queryset = Bicicleta.objects.all()
    serializer_class = BicicletaSerializer
    permission_classes = [AllowAny]

class RepuestoViewSet(viewsets.ModelViewSet):
    queryset = Repuesto.objects.all()
    serializer_class = RepuestoSerializer
    permission_classes = [AllowAny]

class AccesorioViewSet(viewsets.ModelViewSet):
    queryset = Accesorio.objects.all()
    serializer_class = AccesorioSerializer
    permission_classes = [AllowAny]