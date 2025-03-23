# forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Venta
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.core.files import File
from django.forms import inlineformset_factory
from .models import DetalleVenta,Empleado,DivisionEmpleado,Cliente,ProductoRetornable

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

# Validaciones para inicio de sesión
class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_attempt = True

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                self.first_attempt = False
                if not User.objects.filter(email=email).exists():
                    self.add_error('email', "El correo electrónico no existe.")
                else:
                    self.add_error('password', "La contraseña es incorrecta.")
            elif not user.is_active:
                self.first_attempt = False
                raise forms.ValidationError("Esta cuenta está inactiva.")
        return cleaned_data

# Validaciones para registrar nuevo usuario

class CustomUserCreationForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido', 'apellidoM', 'is_active', 'is_staff','is_superuser', 'password1', 'password2', 'groups')
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckActive'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckStaff'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckSuperuser'}),
            }
        labels = {
            'apellido': 'Apellido P.',
            'apellidoM': 'Apellido M.',
        }
        
        
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if len(password1) < 8:
            raise ValidationError(_("La contraseña debe tener al menos 8 caracteres."))

        if not any(char.isupper() for char in password1):
            raise ValidationError(_("La contraseña debe contener al menos una mayúscula."))

        if password1.isdigit():
            raise ValidationError(_("La contraseña no puede consistir solo en números."))

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden."))

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico."))

        return email
    
  
# Formulario para actualizar usuario
class CustomClearableFileInput(forms.ClearableFileInput):
   
    pass

class CustomUserChangeForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido', 'apellidoM', 'imagen', 'dni', 'fecha_nac', 'is_active', 'is_staff', 'is_superuser', 'groups')
        widgets = {
            'imagen': CustomClearableFileInput(),
            'fecha_nac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckActive'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckStaff'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckSuperuser'}),
        }
        labels = {
            'nombre': 'Nombres.',
            'apellido': 'Apellido Paterno',
            'apellidoM': 'Apellido Materno',
            'fecha_nac': 'Fecha de Nacimiento',
        }


class EmpleadorutForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['domicilio', 'division']  
        labels = {
            'division': 'Seleccionar Ruta',}
        
        
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['negocio', 'contacto', 'imagen']
        widgets = {
            'negocio': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }        
                     

class VentaForm(forms.ModelForm):
    productos = forms.ModelMultipleChoiceField(
        queryset=ProductoRetornable.objects.filter(estado='Disponible'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'btn-check'}),
        required=True,
    )
    anticipo = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )

    class Meta:
        model = Venta
        fields = ['cliente', 'productos', 'anticipo', 'saldo_pendiente', 'total']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'saldo_pendiente': forms.HiddenInput(),  
            'total': forms.HiddenInput(),  
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar productos retornables con estado 'Disponible'
        productos_disponibles = ProductoRetornable.objects.filter(estado='Disponible')
        

        # Agrupar productos por tipo de producto y añadir el precio
        grouped_products = {}
        for producto in productos_disponibles:
            tipo = producto.tipo_producto.nombre
            if tipo not in grouped_products:
                grouped_products[tipo] = []
            grouped_products[tipo].append(
                (producto.id, f"{producto.descripcion} - {producto.precio:.2f} bs.")
            )

        # Crear las opciones agrupadas en formato para CheckboxSelectMultiple
        grouped_choices = []
        for tipo, productos in grouped_products.items():
            grouped_choices.append((tipo, productos))

        # Establecer las opciones agrupadas para el campo 'productos'
        self.fields['productos'].widget.choices = grouped_choices

        # Configurar el queryset de clientes
        self.fields['cliente'].queryset = Cliente.objects.all()
            
        
"""class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente','empleado', 'productos', 'anticipo']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'productos': forms.CheckboxSelectMultiple(),
            'anticipo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)"""

        
        
        
        

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all()
        
class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['usuario', 'domicilio', 'division']
        widgets = {
            'division': forms.Select(attrs={'class': 'form-control'}),
        }
        
from .models import ProductosiRetornable, ProductonoRetornable, Producto

class ProductoRetornableForm(forms.ModelForm):
    class Meta:
        model = ProductosiRetornable
        fields = ['descripcion', 'tipo_producto', 'estado', 'precio']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_producto': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'descripcion': 'codigo producto'
        }
        
        


class ProductoForm(forms.ModelForm):
    class Meta:
        model = ProductonoRetornable
        fields = ['tipo_producto', 'stock', 'precio']
        widgets = {
            'tipo_producto': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class ProductosiRetornableForm(forms.ModelForm):
    class Meta:
        model = ProductosiRetornable
        fields = ['descripcion', 'tipo_producto', 'estado', 'precio']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_producto_retornable_descripcion'
            }),
            'tipo_producto': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_producto_retornable_tipo'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_producto_retornable_estado'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_producto_retornable_precio'
            }),
        }
        labels = {
            'descripcion': 'Código Producto'
        }


class ProductonoRetornableForm(forms.ModelForm):
    class Meta:
        model = ProductonoRetornable
        fields = ['tipo_producto', 'stock', 'precio']
        widgets = {
            'tipo_producto': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_producto_no_retornable_tipo'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_producto_no_retornable_stock'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_producto_no_retornable_precio'
            }),
        }
        
        
from .models import TipoProducto, Location, DivisionEmpleado, GastoDiario

class TipoProductoForm(forms.ModelForm):
    class Meta:
        model = TipoProducto
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre del Tipo de Producto',
        }
        
class CambiarEstadoForm(forms.Form):
    productos = forms.ModelMultipleChoiceField(
        queryset=ProductosiRetornable.objects.filter(estado="Ocupado"),
        widget=forms.CheckboxSelectMultiple(),
        required=True,
        label="Selecciona los productos para cambiar su estado"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar los widgets de cada checkbox
        self.fields["productos"].widget.attrs.update({"class": "form-check-input"})
    
from .models import Location, DivisionEmpleado

class RutaForm(forms.Form):
    location_inicial = forms.ModelChoiceField(queryset=Location.objects.all(), label="Ubicación Inicial")
    numero_rutas = forms.IntegerField(min_value=1, max_value=5, label="Número de Rutas")
    rutas = forms.ModelMultipleChoiceField(queryset=DivisionEmpleado.objects.all(), label="Seleccionar Rutas") 

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['cliente', 'latitude', 'longitude','ruta']

class DivisionEmpleadoForm(forms.ModelForm):
    class Meta:
        model = DivisionEmpleado
        fields = ['ruta']
        labels = {
            'ruta': 'Ingresar Nueva Ruta',
        }

class GastoDiarioForm(forms.ModelForm):
    class Meta:
        model = GastoDiario
        fields = ['descripcion', 'monto']
        
        


from django import forms
from decimal import Decimal
from .models import Cliente, Empleado, ProductonoRetornable, ProductosiRetornable

class RegistroVentaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), label="Cliente", required=True)
    anticipo = forms.DecimalField(label="Anticipo", required=False, min_value=0, initial=Decimal('0.00'))
    saldo_pendiente = forms.DecimalField(
        label="Saldo Pendiente",
        required=True,
        min_value=0,
        initial=Decimal('0.00'),
        widget=forms.HiddenInput()  # Campo oculto
    )
    deuda_anterior = forms.DecimalField(
        label="Deuda Anterior",
        required=True,
        min_value=0,
        initial=Decimal('0.00'),
        widget=forms.HiddenInput()  # Campo oculto
    )
    total = forms.DecimalField(
        label="Total",
        required=True,
        min_value=0,
        initial=Decimal('0.00'),
        widget=forms.HiddenInput()  # Campo oculto
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar dinámicamente los productos y sus cantidades al formulario
        for producto in ProductonoRetornable.objects.all():
            self.fields[f'producto_no_retornable_{producto.id}'] = forms.BooleanField(
                required=False, label=f'{producto.tipo_producto.nombre} - ${producto.precio}'
            )
            self.fields[f'cantidad_no_retornable_{producto.id}'] = forms.IntegerField(
                required=False, min_value=0, initial=0, label="Cantidad"
            )

        for producto in ProductosiRetornable.objects.all():
            self.fields[f'producto_retornable_{producto.id}'] = forms.BooleanField(
                required=False, label=f'{producto.descripcion} ({producto.tipo_producto.nombre}) - ${producto.precio}'
            )
            self.fields[f'cantidad_retornable_{producto.id}'] = forms.IntegerField(
                required=False, min_value=0, initial=0, label="Cantidad"
            )

    def clean_anticipo(self):
        anticipo = self.cleaned_data.get('anticipo')
        return anticipo if anticipo else Decimal('0.00')
    
    
class EmpleadoProductoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['productosasignados']
        widget=forms.CheckboxSelectMultiple(),