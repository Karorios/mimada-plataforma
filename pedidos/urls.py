from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear-detalle/', views.crear_detalle, name='crear_detalle'),
]