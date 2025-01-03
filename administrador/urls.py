"""
URL configuration for administrador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from servicio import views
from servicio.views import   VentaDetailView, home, custom_login, custom_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    path('registro_venta/', views.registrar_venta, name='registro_venta'),
    
    #users
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'), 
    

    path('ventas/list', views.venta_list, name='venta_list'),
    #path('ventas/nueva/', VentaCreateView.as_view(), name='venta_create'),
    path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),
    path('ventas/nueva/', views.crear_venta, name='venta_create'),
    path('venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    
    #login
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    
    # Producto Retornable
    path('productos/listar/', views.listar_productos, name='listar_productos'),
    path('producto-retornable/crear/', views.crear_producto_retornable, name='crear_producto_retornable'),
    path('producto-retornable/editar/<int:pk>/', views.editar_producto_retornable, name='editar_producto_retornable'),
    
    # Producto
    
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    
    
    path('combined-list/', views.combined_list_view, name='combined_list'),
    path('tipo-productos/create/', views.TipoProductoCreateView.as_view(), name='tipo_producto_create'),
    path('tipo-productos/<int:pk>/edit/', views.TipoProductoUpdateView.as_view(), name='tipo_producto_edit'),

   
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_edit'),

  
    path('division-empleados/create/', views.DivisionEmpleadoCreateView.as_view(), name='division_empleado_create'),
    path('division-empleados/<int:pk>/edit/', views.DivisionEmpleadoUpdateView.as_view(), name='division_empleado_edit'),

   
    path('gasto-diarios/create/', views.GastoDiarioCreateView.as_view(), name='gasto_diario_create'),
    path('gasto-diarios/<int:pk>/edit/', views.GastoDiarioUpdateView.as_view(), name='gasto_diario_edit'),
    
]

# Sirve los archivos estáticos y multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

