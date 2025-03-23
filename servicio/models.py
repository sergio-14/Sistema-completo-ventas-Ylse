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
        return f"{self.descripcion} - {self.precio:.2f}"

class Producto(models.Model):  
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.tipo_producto.nombre} - ${self.precio:.2f}"

# Modelo de Clientes
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    negocio = models.CharField(max_length=100)
    contacto = models.CharField(max_length=15)
    imagen = models.ImageField(upload_to='clientes/', blank=True, null=True)
    
    def __str__(self):
        return self.negocio
    
class DivisionEmpleado(models.Model):
    ruta = models.CharField(max_length=50)

    def __str__(self):
        return self.ruta
    
class Location(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, related_name='locacion')
    latitude = models.FloatField()
    longitude = models.FloatField()
    ruta = models.ForeignKey(DivisionEmpleado, on_delete=models.SET_NULL, null=True, blank=True, related_name='locations')


    def __str__(self):
        return self.cliente.negocio
 
    
    
class ProductoBase(models.Model):
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True

class ProductonoRetornable(ProductoBase):
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.tipo_producto.nombre}"

class ProductosiRetornable(ProductoBase):
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Ocupado', 'Ocupado'),
        ('Dañado', 'Dañado'),
    ]
    descripcion = models.CharField(max_length=30)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Disponible')

    def __str__(self):
        return f"{self.descripcion} ({self.tipo_producto.nombre})"
    
class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado')
    domicilio = models.TextField()
    division = models.ForeignKey(DivisionEmpleado, on_delete=models.CASCADE)
    productosasignados = models.ManyToManyField(ProductosiRetornable, blank=True)
   
    def __str__(self):
        return f"{self.usuario.nombre} - {self.division.ruta}"
    
    
class GastoDiario(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='gastos')

    def __str__(self):
        return f"{self.empleado}: {self.descripcion}"
    
class RegistroVenta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    anticipo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    deuda_anterior = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.cliente.negocio}"



from django.core.exceptions import ValidationError

class RegistroDetalleVenta(models.Model):
    venta = models.ForeignKey('RegistroVenta', on_delete=models.CASCADE, related_name='detalles')
    producto_no_retornable = models.ForeignKey(ProductonoRetornable, on_delete=models.CASCADE, null=True, blank=True)
    producto_retornable = models.ForeignKey(ProductosiRetornable, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio al momento de la venta
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Validación de producto no retornable y cantidad válida
        if self.producto_no_retornable and self.cantidad:
            if self.producto_no_retornable.stock < self.cantidad:
                raise ValidationError(f"No hay suficiente stock disponible. Stock actual: {self.producto_no_retornable.stock}")
            
            # Descontar stock solo cuando se está creando el registro
            if not self.pk:
                self.producto_no_retornable.stock -= self.cantidad
                self.producto_no_retornable.save()

        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Restaurar stock al eliminar el detalle de la venta
        if self.producto_no_retornable and self.cantidad:
            self.producto_no_retornable.stock += self.cantidad
            self.producto_no_retornable.save()

        super().delete(*args, **kwargs)

    def __str__(self):
        if self.producto_no_retornable:
            return f"Venta {self.venta.id} - Producto {self.producto_no_retornable} x {self.cantidad}"
        elif self.producto_retornable:
            return f"Venta {self.venta.id} - Producto {self.producto_retornable} x {self.cantidad}"
        else:
            return f"Venta {self.venta.id} - Producto desconocido x {self.cantidad}"
        
        
        
        



class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    anticipo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)    
    productos = models.ManyToManyField(ProductoRetornable, related_name='ventas')
    
    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.cliente.negocio}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey('Venta', on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    

    def __str__(self):
        return f"Venta {self.venta.id} - Producto {self.producto.id} ({self.cantidad})"