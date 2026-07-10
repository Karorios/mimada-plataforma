# proveedores/urls.py
from django.urls import path
from django.shortcuts import render

app_name = 'pedidosadmin'

def placeholder(request):
    return render(request, 'placeholder.html', {'seccion': 'pedidosadmin'})

urlpatterns = [
    path('', placeholder, name='dashboard'),
]