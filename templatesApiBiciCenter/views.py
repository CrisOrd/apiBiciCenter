from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db.models import Sum
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import OrdenCompraSerializer 

from .models import (
    Bicicleta, Repuesto, Accesorio, CarritoItem,
    BicicletaCliente, ServicioMantenimiento, OrdenMantenimiento, OrdenCompra, DetalleOrden
)
from .serializers import (
    BicicletaSerializer, RepuestoSerializer, AccesorioSerializer,
    UserSerializer, CarritoItemSerializer, BicicletaClienteSerializer,
    ServicioMantenimientoSerializer, OrdenMantenimientoSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    rut = ''
    telefono = ''
    direccion = ''
    try:
        perfil = user.cliente_perfil 
        rut = perfil.rut
        telefono = perfil.telefono
        direccion = perfil.direccion
    except Exception:
        pass
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'rut': rut,
        'telefono': telefono,
        'direccion': direccion
    }
    
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny]) 
def logout_user(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Ok'}, status=200)
    except:
        return Response({'error': 'Error'}, status=400)


class BicicletaViewSet(viewsets.ModelViewSet):
    queryset = Bicicleta.objects.all()
    serializer_class = BicicletaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class RepuestoViewSet(viewsets.ModelViewSet):
    queryset = Repuesto.objects.all()
    serializer_class = RepuestoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class AccesorioViewSet(viewsets.ModelViewSet):
    queryset = Accesorio.objects.all()
    serializer_class = AccesorioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CarritoViewSet(viewsets.ModelViewSet):
    serializer_class = CarritoItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = CarritoItem.objects.filter(usuario=user)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        total = 0
        for item in queryset:
            try:
                total += item.get_subtotal()
            except Exception:
                pass

        data = {
            'items': serializer.data,
            'subtotal': total,
            'total': total
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        tipo = request.data.get('tipo_producto')
        pid = request.data.get('producto_id')
        try:
            cant = int(request.data.get('cantidad', 1))
        except:
            cant = 1

        producto_real = None
        modelo = None

        if tipo == 'bicicleta':
            modelo = Bicicleta
        elif tipo == 'repuesto':
            modelo = Repuesto
        elif tipo == 'accesorio':
            modelo = Accesorio
        
        if modelo:
            producto_real = modelo.objects.filter(id=pid).first()
        
        if not producto_real:
            return Response({'error': 'Producto no encontrado'}, status=404)

        if producto_real.stock < cant:
            return Response({'error': 'No hay stock suficiente'}, status=400)

        item_existente = CarritoItem.objects.filter(
            usuario=request.user, 
            tipo_producto=tipo, 
            producto_id=pid
        ).first()

        if item_existente:
            nuevo_total = item_existente.cantidad + cant
            
            if nuevo_total > producto_real.stock:
                 return Response({'error': 'No hay stock suficiente para agregar más'}, status=400)

            item_existente.cantidad = nuevo_total
            item_existente.save()
            return Response({'success': True, 'message': 'Cantidad actualizada'})
        else:
            CarritoItem.objects.create(
                usuario=request.user,
                tipo_producto=tipo,
                producto_id=pid,
                cantidad=cant
            )
            return Response({'success': True, 'message': 'Agregado al carrito'}, status=201)

    @action(detail=False, methods=['delete'])
    def vaciar(self, request):
        self.get_queryset().delete()
        return Response({'success': True})

    @action(detail=False, methods=['post'])
    def pago(self, request):
        carrito = self.get_queryset()
        if not carrito.exists():
            return Response({'error': 'El carrito está vacío'}, status=400)

        try:
            total_orden = sum(item.get_subtotal() for item in carrito)
            nueva_orden = OrdenCompra.objects.create(
                usuario=request.user,
                total=total_orden
            )
            for item in carrito:
                producto_real = item.get_producto()
                if producto_real:
                    if producto_real.stock >= item.cantidad:
                        producto_real.stock -= item.cantidad
                        producto_real.save()
                    else:
                        nueva_orden.delete()
                        return Response({'error': f'Stock insuficiente para {producto_real.nombre}'}, status=400)
                DetalleOrden.objects.create(
                    orden=nueva_orden,
                    producto_nombre=producto_real.nombre if producto_real else "Producto Eliminado",
                    tipo_producto=item.tipo_producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.get_precio_unitario(),
                    subtotal=item.get_subtotal()
                )
            carrito.delete()
            
            return Response({
                'success': True, 
                'message': 'Compra exitosa. Historial guardado.', 
                'data': {'total': total_orden, 'orden_id': nueva_orden.id}
            })

        except Exception:
            return Response({'error': 'Error interno al procesar el pago'}, status=500)
    
class BicicletaClienteViewSet(viewsets.ModelViewSet):
    queryset = BicicletaCliente.objects.all()
    serializer_class = BicicletaClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return BicicletaCliente.objects.all()
        return BicicletaCliente.objects.filter(cliente=user)
        

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

class ServicioMantenimientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServicioMantenimiento.objects.all()
    serializer_class = ServicioMantenimientoSerializer
    permission_classes = [IsAuthenticated]

class OrdenMantenimientoViewSet(viewsets.ModelViewSet):
    queryset = OrdenMantenimiento.objects.all()
    serializer_class = OrdenMantenimientoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return OrdenMantenimiento.objects.all()
        return OrdenMantenimiento.objects.filter(cliente=user)
    
class OrdenesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrdenCompra.objects.filter(usuario=self.request.user).order_by('-fecha_compra')