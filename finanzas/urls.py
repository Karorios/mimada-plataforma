from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('abono/nuevo/', views.registrar_abono, name='abono_crear'),
    path('abono/nuevo/<int:pedido_id>/', views.registrar_abono, name='abono_crear_pedido'),
]