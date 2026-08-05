from django.urls import path
from . import views

app_name = 'pedidosadmin'

urlpatterns = [
    path('', views.lista_pedidos, name='dashboard'),
    path('<int:pk>/', views.detalle_pedido, name='detalle'),
]