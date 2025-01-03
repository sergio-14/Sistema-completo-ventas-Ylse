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
    ventas = Venta.objects.all()
    gastos = GastoDiario.objects.all()

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

def crear_venta(request):
    # Crear un formset para los detalles de la venta
    DetalleVentaFormSet = formset_factory(DetalleVentaForm, extra=0)
    
    # Si el formulario es enviado con datos POST
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            venta = form.save(commit=False)  # No guardar aún en la base de datos
            
            # Obtener los productos retornables seleccionados
            productos_seleccionados_retornable = form.cleaned_data['productos']
            anticipo = form.cleaned_data['anticipo']
            
            # Calcular el total de productos retornables y saldo pendiente
            totalretornable = sum([producto.precio for producto in productos_seleccionados_retornable])
            saldo_pendienteretorable = totalretornable - anticipo

            # Guardar la venta primero para obtener su ID
            venta.save()  # Aquí se guarda la venta para obtener el ID
            
            # Asignamos total y saldo pendiente a la venta
            venta.total = totalretornable  # Inicializamos el total con los productos retornables
            venta.saldo_pendiente = saldo_pendienteretorable  # Inicializamos el saldo pendiente
            venta.save()  # Guardar la venta con los valores iniciales
            
            # Asociar los productos retornables a la venta
            venta.productos.set(productos_seleccionados_retornable)
            
            # Actualizar el estado de los productos retornables a 'Ocupado'
            for producto in productos_seleccionados_retornable:
                producto.estado = 'Ocupado'
                producto.save()  # Guardamos el cambio en el estado del producto
            
            # Procesar los detalles de los productos no retornables desde el formset
            total_no_retornable = 0
            productos_seleccionados = []  
            for detalle_form in formset:
                if detalle_form.cleaned_data:
                    producto = detalle_form.cleaned_data['producto']
                    cantidad = detalle_form.cleaned_data['cantidad']
                    subtotal = producto.precio * cantidad
                    total_no_retornable += subtotal  # Sumar al total de productos no retornables
                    
                    # Crear el detalle de la venta con el subtotal calculado
                    DetalleVenta.objects.create(
                        venta=venta,  # Usar la venta ya guardada
                        producto=producto,
                        cantidad=cantidad,
                        subtotal=subtotal
                    )
                    
                    # Añadir el producto seleccionado a la lista de productos
                    productos_seleccionados.append(producto)
            
            # Sumar el total de los productos no retornables al total de la venta
            venta.total += total_no_retornable  # Sumar el total de los productos no retornables
            
            # Actualizar el saldo pendiente con el total completo de la venta
            venta.saldo_pendiente = venta.total - venta.anticipo
            venta.save()  # Guardar la venta con el total actualizado
            
            # Redirigir a la lista de ventas
            return redirect('venta_list')  
    else:
        form = VentaForm()  # Si el método no es POST, inicializar el formulario
        formset = DetalleVentaFormSet()  # Inicializar el formset
    
    # Obtener todos los productos disponibles
    productos = Producto.objects.all()
    
    # Renderizar la plantilla con los formularios y productos disponibles
    return render(request, 'ventas/venta_form.html', {
        'form': form,
        'formset': formset,
        'productos': productos,
    })
    

def registrar_venta(request):
    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)  # No guarda aún para poder modificar algunos campos
            productos_seleccionados_retornable = form.cleaned_data['productos']
            anticipo = form.cleaned_data['anticipo']
            
            # Cálculo del total y saldo pendiente
            totalretornable = sum([producto.precio for producto in productos_seleccionados_retornable])
            saldo_pendienteretorable = totalretornable - anticipo
            
            # Asignamos total y saldo pendiente a la venta
            venta.total = totalretornable
            venta.saldo_pendiente = saldo_pendienteretorable
            
            # Guardamos la venta
            venta.save()
            venta.productos.set(productos_seleccionados_retornable)  # Asociar los productos a la venta

            # Actualizar el estado de los productos a 'Ocupado'
            for producto in productos_seleccionados_retornable:
                producto.estado = 'Ocupado'
                producto.save()  # Guardamos el cambio en el estado del producto

            return redirect('venta_list')  # Redirigir a una vista de lista de ventas o alguna otra
    else:
        form = VentaForm()

    return render(request, 'registro_venta.html', {'form': form})

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