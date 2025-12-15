from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

TIPOS_BICICLETA = [
    ('mountain', 'Montaña'),
    ('road', 'Ruta'),
    ('hybrid', 'Híbrida'),
    ('bmx', 'BMX'),
    ('electric', 'Eléctrica'),
    ('folding', 'Plegable'),
    ('cruiser', 'Cruiser'),
    ('city', 'Urbana'),
]

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_perfil')
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.rut}"

class Bicicleta(models.Model):
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100) 
    modelo = models.CharField(max_length=255)
    descripcion = models.TextField()     
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    imagen = models.ImageField(upload_to='bicicletas/') 
    tipo = models.CharField(max_length=50, choices=TIPOS_BICICLETA, default='city')
    color = models.CharField(max_length=20)   
    stock = models.IntegerField(default=0)    
    class Meta:
        db_table = 'menu_bicicleta'

    def __str__(self):
        return f"{self.nombre} {self.marca}"

class Repuesto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField() 
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    imagen = models.ImageField(upload_to='repuestos/') 
    categoria = models.CharField(max_length=100) 
    marca = models.CharField(max_length=100)     
    numero_parte = models.CharField(max_length=100) 
    compatibilidad = models.TextField() 
    stock = models.IntegerField(default=0)

    class Meta:
        db_table = 'menu_repuesto'

    def __str__(self):
        return self.nombre
    
class OrdenCompra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"


class DetalleOrden(models.Model):
    orden = models.ForeignKey(OrdenCompra, related_name='detalles', on_delete=models.CASCADE)
    producto_nombre = models.CharField(max_length=255)
    tipo_producto = models.CharField(max_length=50)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto_nombre}"

class Accesorio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    imagen = models.ImageField(upload_to='accesorios/') 
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)      
    stock = models.IntegerField(default=0)

    class Meta:
        db_table = 'menu_accesorio'

    def __str__(self):
        return self.nombre

class CarritoItem(models.Model):
    TIPO_CHOICES = [
        ('bicicleta', 'Bicicleta'),
        ('repuesto', 'Repuesto'),
        ('accesorio', 'Accesorio'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_producto = models.CharField(max_length=20, choices=TIPO_CHOICES)
    producto_id = models.IntegerField()
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'tipo_producto', 'producto_id')
    
    def get_producto(self):
        if self.tipo_producto == 'bicicleta':
            return Bicicleta.objects.filter(id=self.producto_id).first()
        elif self.tipo_producto == 'repuesto':
            return Repuesto.objects.filter(id=self.producto_id).first()
        elif self.tipo_producto == 'accesorio':
            return Accesorio.objects.filter(id=self.producto_id).first()
        return None
    
    def get_precio_unitario(self):
        producto = self.get_producto()
        if producto:
            return producto.precio
        return 0

    def get_subtotal(self):
        return self.get_precio_unitario() * self.cantidad
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_producto}"
    
class BicicletaCliente(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    anio = models.IntegerField(null=True, blank=True)
    notas_adicionales = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.marca} - {self.cliente.username}"

class ServicioMantenimiento(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class OrdenMantenimiento(models.Model):
    ESTADOS = [('pendiente', 'Pendiente'), ('completado', 'Completado')]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    bicicleta = models.ForeignKey(BicicletaCliente, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(ServicioMantenimiento)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Orden #{self.id} - {self.cliente.username}"