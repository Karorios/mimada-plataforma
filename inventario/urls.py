# inventario/urls.py
from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'inventario'


urlpatterns = [
    path('', views.inventario_dashboard, name='dashboard'),
    path('agregar/', views.item_crear, name='item_crear'),
    path('editar/<int:pk>/', views.item_editar, name='item_editar'),
    path('eliminar/<int:pk>/', views.item_eliminar, name='item_eliminar'),
    path('categoria/agregar/', views.categoria_crear, name='categoria_crear'),
    path('categoria/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),
    path('categoria/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),
]