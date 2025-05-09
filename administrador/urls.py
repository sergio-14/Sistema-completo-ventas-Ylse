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
from servicio.views import RegistrarVentaView, DetalleVentaView
from servicio.views import   VentaDetailView, home, custom_login, custom_logout
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('mapas/', views.mapas, name='mapas'),
    
    path('venta/<int:venta_id>/pdf/', views.detalle_venta_pdf, name='detalle_venta_pdf'),
    path('ventas/exportar/', views.exportar_excel, name='exportar_excel'),
    
    
    path('ultima-venta-clientes/', views.ultima_venta_clientes, name='ultima_venta_clientes'),
    path('clientes/ocupados/', views.clientes_ocupados, name='clientes_ocupados'),
    
    path('buscador-cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('registrar-pago/', views.registrar_pago, name='registrar_pago'),
    path('cambiar-estado/', views.cambiar_estado_productos, name='cambiar_estado'),
    
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('empleado/<int:empleado_id>/asignar_productos/', views.asignar_productos, name='asignar_productos'),
    path('empleado/<int:empleado_id>/editar/', views.editar_empleado, name='editar_empleado'),
    
    
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('cliente/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    
    
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('saldo-cliente/<int:cliente_id>/', views.obtener_saldo_cliente, name='obtener_saldo_cliente'),
    path('ventas/saldo-cliente/<int:cliente_id>/', views.obtener_saldo_cliente, name='obtener_saldo_cliente'),
    
    path('crear_venta/', views.crear_venta, name='crear_venta'),
    
    
    
    
    #users
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'), 
    path('usuario/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    

    path('ventas/list', views.venta_list, name='venta_list'),
    path('ventasreporte/listrepo', views.venta_listrepo, name='venta_listrepo'),

    path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta_detail'),

    path('venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    
    #login
   
    path('login/', custom_login, name='custom_login'),
    path('logout/', custom_logout, name='logout'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    
    # Producto Retornable
    path('productos/listar/', views.listar_productos, name='listar_productos'),
    path('producto-retornable/crear/', views.crear_producto_retornable, name='crear_producto_retornable'),
    path('producto-retornable/editar/<int:pk>/', views.editar_producto_retornable, name='editar_producto_retornable'),
    
    # Producto
    
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    
    
    path('combined-list/', views.combined_list, name='combined_list'),
    path('combined-lista/', views.combined_lista, name='combined_lista'),
    path('tipo-productos/create/', views.TipoProductoCreateView.as_view(), name='tipo_producto_create'),
    path('tipo-productos/<int:pk>/edit/', views.TipoProductoUpdateView.as_view(), name='tipo_producto_edit'),

   
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_edit'),

  
    path('division-empleados/create/', views.DivisionEmpleadoCreateView.as_view(), name='division_empleado_create'),
    path('division-empleados/<int:pk>/edit/', views.DivisionEmpleadoUpdateView.as_view(), name='division_empleado_edit'),

   
    path('gasto-diarios/create/', views.GastoDiarioCreateView.as_view(), name='gasto_diario_create'),
    path('gasto-diarios/<int:pk>/edit/', views.GastoDiarioUpdateView.as_view(), name='gasto_diario_edit'),
    
    
    path('registrar_venta/', RegistrarVentaView.as_view(), name='registrar_venta'),
    path('detalle_venta/<int:pk>/', DetalleVentaView.as_view(), name='detalle_venta'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

