from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Bicicleta, Repuesto, Accesorio, CarritoItem, 
    BicicletaCliente, ServicioMantenimiento, OrdenMantenimiento,
    Cliente  , OrdenCompra, DetalleOrden
)

class UserSerializer(serializers.ModelSerializer):
    rut = serializers.CharField(write_only=True, required=False, allow_blank=True)
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)
    direccion = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'rut', 'telefono', 'direccion']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        rut_data = validated_data.pop('rut', '')
        telefono_data = validated_data.pop('telefono', '')
        direccion_data = validated_data.pop('direccion', '')
        user = User.objects.create_user(**validated_data)
        Cliente.objects.create(
            user=user,
            rut=rut_data,
            telefono=telefono_data,
            direccion=direccion_data
        )
        return user


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
        
class CarritoItemSerializer(serializers.ModelSerializer):
    precio_unitario = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    producto_nombre = serializers.SerializerMethodField()
    producto_imagen = serializers.SerializerMethodField()
    stock_disponible = serializers.SerializerMethodField()
    
    usuario = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = CarritoItem
        fields = ['id', 'usuario', 'tipo_producto', 'producto_id', 'cantidad', 'precio_unitario', 'subtotal', 'producto_nombre', 'producto_imagen', 'stock_disponible']
        read_only_fields = ['precio_unitario', 'subtotal', 'producto_nombre', 'producto_imagen']

    def get_precio_unitario(self, obj):
        return obj.get_precio_unitario()

    def get_subtotal(self, obj):
        return obj.get_subtotal()

    def get_producto_nombre(self, obj):
        prod = obj.get_producto()
        return str(prod.nombre) if prod else "Producto no disponible"
        
    def get_producto_imagen(self, obj):
        prod = obj.get_producto()
        if prod and prod.imagen:
            return prod.imagen.url
        return ""

    def get_stock_disponible(self, obj):
        prod = obj.get_producto()
        return prod.stock if prod else 0

    def validate(self, data):
        cantidad_nueva = data.get('cantidad')
        if cantidad_nueva is None:
            return data
        if self.instance: 
            producto = self.instance.get_producto()
        else: 
            tipo = data.get('tipo_producto')
            pid = data.get('producto_id')
            # Lógica rápida para encontrar el producto según tipo
            if tipo == 'bicicleta':
                producto = Bicicleta.objects.filter(id=pid).first()
            elif tipo == 'repuesto':
                producto = Repuesto.objects.filter(id=pid).first()
            elif tipo == 'accesorio':
                producto = Accesorio.objects.filter(id=pid).first()
            else:
                producto = None
        if producto:
            if cantidad_nueva > producto.stock:
                raise serializers.ValidationError(
                    f"Stock insuficiente. Solo quedan {producto.stock} unidades."
                )
            if cantidad_nueva < 1:
                raise serializers.ValidationError("La cantidad mínima es 1.")
        
        return data

class BicicletaClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BicicletaCliente
        fields = '__all__'

class ServicioMantenimientoSerializer(serializers.ModelSerializer):
    class Meta: model = ServicioMantenimiento; fields = '__all__'
    
class OrdenMantenimientoSerializer(serializers.ModelSerializer):
    servicios_ids = serializers.ListField(write_only=True)
    
    class Meta: 
        model = OrdenMantenimiento
        fields = '__all__'
        read_only_fields = ['total', 'servicios', 'fecha_creacion'] 

    def create(self, validated_data):
        servicios_ids = validated_data.pop('servicios_ids', [])
        orden = OrdenMantenimiento.objects.create(**validated_data)
        orden.servicios.set(servicios_ids)
        
        total = sum([s.precio for s in orden.servicios.all()])
        orden.total = total
        orden.save()
        return orden
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['servicios'] = ServicioMantenimientoSerializer(instance.servicios.all(), many=True).data
        return response
    
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