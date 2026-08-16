from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
# Catálogo clientes
    path('lista/', views.lista_productos, name='lista'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),

    # Crear producto (ya existe)
    path('crear-producto/', views.crear_producto, name='crear_producto'),

    # Nuevo módulo administrador
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    #para la cantidad
    path('actualizar-listas/<int:pk>/', views.actualizar_listas, name='actualizar_listas'),

path(
    'admin/eliminar/<int:pk>/',
    views.eliminar_producto,
    name='eliminar_producto'
),
path(
    'admin/editar/<int:pk>/',
    views.editar_producto,
    name='editar_producto'
),
path('admin/carrusel/', views.carrusel_dashboard, name='carrusel_dashboard'),
    path('admin/carrusel/crear/', views.crear_item_carrusel, name='crear_item_carrusel'),
    path('admin/carrusel/editar/<int:pk>/', views.editar_item_carrusel, name='editar_item_carrusel'),
    path('admin/carrusel/eliminar/<int:pk>/', views.eliminar_item_carrusel, name='eliminar_item_carrusel'),

]
