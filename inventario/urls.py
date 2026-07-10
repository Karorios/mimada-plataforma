# inventario/urls.py
from django.urls import path
from django.shortcuts import render

app_name = 'inventario'

def placeholder(request):
    return render(request, 'placeholder.html', {'seccion': 'Inventario'})

urlpatterns = [
    path('', placeholder, name='dashboard'),
]