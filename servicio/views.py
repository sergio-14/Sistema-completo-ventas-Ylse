# views.py
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from .models import Venta,Producto,DetalleVenta
from .forms import VentaForm
from .forms import VentaForm, DetalleVentaForm
from django.forms import formset_factory
    
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Prefetch, Count, Q

from django.contrib.auth.models import Group
from django.contrib import messages
from .models import User, Cliente, Empleado,DivisionEmpleado,GastoDiario
from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import ProductoRetornable, Producto
from .forms import ProductoRetornableForm, ProductoForm
from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')

# Listar ventas
def venta_list(request):
    # Obtener todos los registros de Venta y GastoDiario
    ventas = Venta.objects.all().order_by('-fecha') 
    gastos = GastoDiario.objects.all().order_by('-fecha') 

    context = {
        'ventas': ventas,
        'gastos': gastos,
    }
    return render(request, 'ventas/venta_list.html', context)


# seccion usuarios 
def agregar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Asignar grupos
            grupos = form.cleaned_data.get('groups')
            for grupo in grupos:
                user.groups.add(grupo)
            
            # Verificar si es Cliente o Empleado
            tipo = request.POST.get('tipo_usuario')
            if tipo == 'cliente':
                Cliente.objects.create(
                    usuario=user, 
                    negocio=request.POST.get('negocio'), 
                    contacto=request.POST.get('contacto'),
                    imagen=request.FILES.get('imagen')
                )
            elif tipo == 'empleado':
                division_id = request.POST.get('division')
                Empleado.objects.create(
                    usuario=user, 
                    domicilio=request.POST.get('domicilio'), 
                    division_id=division_id
                )
            
            messages.success(request, "Usuario creado exitosamente.")
            return redirect('listar_usuarios')
    else:
        form = CustomUserCreationForm()
    
    # Obtener las divisiones disponibles
    divisiones = DivisionEmpleado.objects.all()
    
    return render(request, 'usuarios/agregar_usuario.html', {'form': form, 'divisiones': divisiones})




def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect('listar_usuarios')
        else:
            # Agregar un mensaje de error si el formulario no es válido
            messages.error(request, "Hubo un error con el formulario.")
            print(form.errors)  # Esto te permitirá ver los errores del formulario en la consola
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'user': user})


def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})


from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import VentaForm

def registrar_venta(request):
    empleado = request.user.empleado  # Obtén el empleado relacionado con el usuario
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.empleado = empleado  # Asigna el empleado automáticamente
            venta.save()  # Guarda la venta
            form.save_m2m()  # Guarda la relación Many-to-Many con productos
            
            # Actualiza el estado de los productos retornables
            for producto in venta.productos.all():
                producto.estado = 'Ocupado'
                producto.save()
            
            return redirect('venta_list')  # Redirige a la lista de ventas
    else:
        form = VentaForm()

    return render(request, 'registrar_venta.html', {'form': form})


@login_required
def obtener_saldo_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    ultima_venta = Venta.objects.filter(cliente=cliente).order_by('-fecha').first()
    saldo_pendiente = float(ultima_venta.saldo_pendiente) if ultima_venta else 0
    return JsonResponse({'saldo_pendiente': saldo_pendiente})




from decimal import Decimal

def crear_venta(request):
    DetalleVentaFormSet = formset_factory(DetalleVentaForm, extra=0)
    empleado = request.user.empleado  # Obtén el empleado relacionado con el usuario

    if request.method == 'POST':
        
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Guardar la venta
            venta = form.save(commit=False)
            venta.empleado = empleado  # Asigna el empleado automáticamente
            venta.save()  # Guarda la venta primero
            form.save_m2m()  # Guarda la relación Many-to-Many con productos

            # Actualizar estado de los productos retornables
            for producto in venta.productos.all():
                producto.estado = 'Ocupado'
                producto.save()

            # Guardar el detalle de la venta
            for detalle_form in formset:
                if detalle_form.cleaned_data:
                    producto = detalle_form.cleaned_data['producto']
                    cantidad = detalle_form.cleaned_data['cantidad']
                    subtotal = cantidad * producto.precio  # Precio del producto desde el modelo

                    # Crear y guardar el detalle de la venta
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        subtotal=subtotal
                    )

            # Redirigir a la lista de ventas
            return redirect('venta_list')
        else:
            # Depuración de errores
            if not form.is_valid():
                print("Errores en el formulario principal:")
                print(form.errors)

            if not formset.is_valid():
                print("Errores en el formset:")
                for detalle_form in formset:
                    print(detalle_form.errors)
    else:
        form = VentaForm()
        formset = DetalleVentaFormSet()

    productos = Producto.objects.values('id', 'tipo_producto__nombre', 'precio')
    return render(request, 'ventas/venta_form.html', {
        'form': form,
        'formset': formset,
        'productos': productos,
    })



from django.http import JsonResponse
from .models import Cliente


    
    



# Ver detalles de venta
class VentaDetailView(DetailView):
    model = Venta
    model = GastoDiario
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta, gasto_diario'
    
def detalle_venta(request, venta_id):
    # Obtiene la venta específica o lanza un error 404 si no existe
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtiene los detalles asociados a la venta
    detalles = venta.detalles.select_related('producto', 'producto__tipo_producto')

    # Pasamos la venta y sus detalles al contexto
    return render(request, 'detalle_venta.html', {
        'venta': venta,
        'detalles': detalles,
    })
    
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

#productos
# Listar Productos
def listar_productos(request):
    productos_retornables_list = ProductoRetornable.objects.all()
    productos_list = Producto.objects.all()
    paginator_retornables = Paginator(productos_retornables_list, 5) 
    paginator_productos = Paginator(productos_list, 1)  

    page_number_retornables = request.GET.get('page_retornables')
    page_number_productos = request.GET.get('page_productos')

    page_retornables = paginator_retornables.get_page(page_number_retornables)
    page_productos = paginator_productos.get_page(page_number_productos)

    return render(request, 'productos/listar_productos.html', {
        'page_retornables': page_retornables,
        'page_productos': page_productos,
    })
    
# Crear ProductoRetornable
def crear_producto_retornable(request):
    if request.method == 'POST':
        form = ProductoRetornableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoRetornableForm()
    return render(request, 'productos/formulario_re.html', {'form': form})

# Editar ProductoRetornable
def editar_producto_retornable(request, pk):
    producto = get_object_or_404(ProductoRetornable, pk=pk)
    if request.method == 'POST':
        form = ProductoRetornableForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoRetornableForm(instance=producto)
    return render(request, 'productos/formulario_re.html', {'form': form})

# Crear Producto
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/formulario_de.html', {'form': form})

# Editar Producto
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/formulario_de.html', {'form': form})



from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import TipoProducto, Location, DivisionEmpleado, GastoDiario
from .forms import TipoProductoForm, LocationForm, DivisionEmpleadoForm, GastoDiarioForm

def combined_list_view(request):
    # Pagination for TipoProducto
    tipo_producto_list = TipoProducto.objects.all()
    tipo_producto_paginator = Paginator(tipo_producto_list, 2)  # Adjust items per page
    tipo_producto_page = request.GET.get('tipo_producto_page')
    tipo_producto = tipo_producto_paginator.get_page(tipo_producto_page)

    # Pagination for Location
    location_list = Location.objects.all()
    location_paginator = Paginator(location_list, 2)  # Adjust items per page
    location_page = request.GET.get('location_page')
    locations = location_paginator.get_page(location_page)

    # Pagination for DivisionEmpleado
    division_empleado_list = DivisionEmpleado.objects.all()
    division_empleado_paginator = Paginator(division_empleado_list, 2)  # Adjust items per page
    division_empleado_page = request.GET.get('division_empleado_page')
    division_empleados = division_empleado_paginator.get_page(division_empleado_page)

    context = {
        'tipo_producto': tipo_producto,
        'locations': locations,
        'division_empleados': division_empleados,
    }
    return render(request, 'funciones/combined_list.html', context)


class TipoProductoCreateView(CreateView):
    model = TipoProducto
    form_class = TipoProductoForm
    template_name = 'funciones/tipo_producto_form.html'
    success_url = reverse_lazy('combined_list')

class TipoProductoUpdateView(UpdateView):
    model = TipoProducto
    form_class = TipoProductoForm
    template_name = 'funciones/tipo_producto_form.html'
    success_url = reverse_lazy('combined_list')



class LocationCreateView(CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'funciones/location_form.html'
    success_url = reverse_lazy('combined_list')

class LocationUpdateView(UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'funciones/location_form.html'
    success_url = reverse_lazy('combined_list')



class DivisionEmpleadoCreateView(CreateView):
    model = DivisionEmpleado
    form_class = DivisionEmpleadoForm
    template_name = 'funciones/division_empleado_form.html'
    success_url = reverse_lazy('combined_list_view')

class DivisionEmpleadoUpdateView(UpdateView):
    model = DivisionEmpleado
    form_class = DivisionEmpleadoForm
    template_name = 'funciones/division_empleado_form.html'
    success_url = reverse_lazy('combined_list_view')
    


class GastoDiarioCreateView(CreateView):
    model = GastoDiario
    form_class = GastoDiarioForm
    template_name = 'gastos/gasto_diario_form.html'
    success_url = reverse_lazy('venta_list')

class GastoDiarioUpdateView(UpdateView):
    model = GastoDiario
    form_class = GastoDiarioForm
    template_name = 'gastos/gasto_diario_form.html'
    success_url = reverse_lazy('venta_list')