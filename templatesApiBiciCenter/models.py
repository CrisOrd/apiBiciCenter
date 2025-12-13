from django.db import models

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