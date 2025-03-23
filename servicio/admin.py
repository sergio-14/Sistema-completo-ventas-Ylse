from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from .models import User, DetalleVenta
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from . models import Cliente,  Empleado,ProductoRetornable, Producto, GastoDiario,Location, Venta, DivisionEmpleado,TipoProducto
from .forms import CustomUserCreationForm, CustomUserChangeForm

admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'nombre', 'apellido', 'apellidoM',  'get_groups', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido', )
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('nombre', 'apellido','apellidoM', 'imagen', 'dni','fecha_nac','estado')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido','apellidoM', 'is_active', 'is_staff', 'is_superuser', 'password1', 'password2', 'groups'),
        }),
    )

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Grupo'

from .models import RegistroDetalleVenta, RegistroVenta, ProductosiRetornable, ProductonoRetornable

admin.site.register(User, CustomUserAdmin)

admin.site.register(Cliente)
admin.site.register(Empleado)
admin.site.register(Venta)
admin.site.register(ProductoRetornable)
admin.site.register(Producto)
admin.site.register(DivisionEmpleado)
admin.site.register(TipoProducto)
admin.site.register(GastoDiario)
admin.site.register(Location)
admin.site.register(DetalleVenta)
admin.site.register(RegistroDetalleVenta)
admin.site.register(RegistroVenta)  
admin.site.register(ProductosiRetornable)
admin.site.register(ProductonoRetornable)
