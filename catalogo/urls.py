from django.urls import path
from . import views

app_name = 'catalogo'
urlpatterns = [
    path('lista/', views.lista_productos, name='lista'),
    path('crear-producto/', views.crear_producto, name='crear_producto'),
]