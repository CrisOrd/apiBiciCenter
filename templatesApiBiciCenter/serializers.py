from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import (
    Bicicleta, Repuesto, Accesorio, CarritoItem, 
    OrdenCompra, DetalleOrden, BicicletaCliente, 
    ServicioMantenimiento, OrdenMantenimiento
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class BicicletaSerializer(serializers.ModelSerializer):
    def get_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return reverse('bicicletas-detail', kwargs={'pk': obj.pk}, request=request)
    
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Bicicleta
        fields = '__all__'

class RepuestoSerializer(serializers.ModelSerializer):
    def get_url(self, obj):
        request = self.context.get('request')
        return reverse('repuestos-detail', kwargs={'pk': obj.pk}, request=request)
    
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Repuesto
        fields = '__all__'

class AccesorioSerializer(serializers.ModelSerializer):
    def get_url(self, obj):
        request = self.context.get('request')
        return reverse('accesorios-detail', kwargs={'pk': obj.pk}, request=request)
    
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Accesorio
        fields = '__all__'

class CarritoItemSerializer(serializers.ModelSerializer):
    precio_unitario = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    producto_nombre = serializers.SerializerMethodField()
    producto_imagen = serializers.SerializerMethodField()
    stock_disponible = serializers.SerializerMethodField()
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = CarritoItem
        fields = ['id', 'usuario', 'tipo_producto', 'producto_id', 'cantidad', 
                  'precio_unitario', 'subtotal', 'producto_nombre', 'producto_imagen', 'stock_disponible']
        read_only_fields = ['precio_unitario', 'subtotal', 'producto_nombre', 'producto_imagen']

    def get_precio_unitario(self, obj): return obj.get_precio_unitario()
    def get_subtotal(self, obj): return obj.get_subtotal()
    
    def get_producto_nombre(self, obj):
        prod = obj.get_producto()
        return str(prod.nombre) if prod else "Producto no disponible"
        
    def get_producto_imagen(self, obj):
        prod = obj.get_producto()
        if prod and prod.imagen: return prod.imagen.url
        return ""

    def get_stock_disponible(self, obj):
        prod = obj.get_producto()
        return prod.stock if prod else 0

    def validate(self, data):
        cantidad_nueva = data.get('cantidad')
        if cantidad_nueva is None: return data

        if self.instance:
            producto = self.instance.get_producto()
        else:
            tipo = data.get('tipo_producto')
            pid = data.get('producto_id')
            if tipo == 'bicicleta': producto = Bicicleta.objects.filter(id=pid).first()
            elif tipo == 'repuesto': producto = Repuesto.objects.filter(id=pid).first()
            elif tipo == 'accesorio': producto = Accesorio.objects.filter(id=pid).first()
            else: producto = None

        if producto:
            if cantidad_nueva > producto.stock:
                raise serializers.ValidationError(f"Stock insuficiente. Quedan {producto.stock}.")
            if cantidad_nueva < 1:
                raise serializers.ValidationError("Mínimo 1 unidad.")
        return data

class DetalleOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleOrden
        fields = ['producto_nombre', 'tipo_producto', 'cantidad', 'precio_unitario', 'subtotal']

class OrdenCompraSerializer(serializers.ModelSerializer):
    detalles = DetalleOrdenSerializer(many=True, read_only=True)
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = OrdenCompra
        fields = ['id', 'usuario', 'fecha_compra', 'total', 'detalles']

class BicicletaClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BicicletaCliente
        fields = '__all__'
        read_only_fields = ['cliente']

class ServicioMantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioMantenimiento
        fields = '__all__'

class OrdenMantenimientoSerializer(serializers.ModelSerializer):
    servicios = serializers.PrimaryKeyRelatedField(many=True, queryset=ServicioMantenimiento.objects.all())
    
    class Meta:
        model = OrdenMantenimiento
        fields = '__all__'
        read_only_fields = ['fecha_recepcion']

