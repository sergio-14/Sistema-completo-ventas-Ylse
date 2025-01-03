from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo de correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    imagen = models.ImageField(upload_to='path/to/upload', null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    apellidoM = models.CharField(max_length=50, null=True, blank=True)
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Carnet Identidad:')
    fecha_nac = models.DateField(null=True, blank=True)
    estado = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
 
    # Añade los campos para las relaciones de grupos y permisos
    groups = models.ManyToManyField(Group, blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='user_permissions')
    
    # Campos para la fecha de creación y modificación
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return f'{self.nombre} {self.apellido} {self.apellidoM}'

   
    
class TipoProducto(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class ProductoRetornable(models.Model):
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Ocupado', 'Ocupado'),
        ('Dañado', 'Dañado'),
    ]
    descripcion = models.CharField(max_length=30)
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Disponible')
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Producto {self.id} - {self.tipo_producto.nombre}"

class Producto(models.Model):  
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.tipo_producto.nombre} - {self.stock} unidades"

# Modelo de Clientes
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    negocio = models.CharField(max_length=100)
    contacto = models.CharField(max_length=15)
    imagen = models.ImageField(upload_to='clientes/', blank=True, null=True)
    
    def __str__(self):
        return self.negocio
    
class Location(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, related_name='locacion')
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.cliente.negocio



class DivisionEmpleado(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado')
    domicilio = models.TextField()
    division = models.ForeignKey(DivisionEmpleado, on_delete=models.CASCADE)
   
    def __str__(self):
        return f"{self.usuario.nombre} {self.usuario.apellido} - {self.division.nombre}"

class GastoDiario(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='gastos')

    def __str__(self):
        return f"{self.empleado}: {self.descripcion}"
    


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    anticipo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)    
    productos = models.ManyToManyField(ProductoRetornable, related_name='ventas')
    
    

    def __str__(self):
        return f"{self.cliente.negocio} - {self.fecha}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey('Venta', on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta {self.venta.id} - Producto {self.producto.id} ({self.cantidad})"