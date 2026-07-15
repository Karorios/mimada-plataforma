# proveedores/urls.py
from django.urls import path
from django.shortcuts import render

app_name = 'panelprincipaladmin'

def placeholder(request):
    return render(request, 'placeholder.html', {'seccion': 'panelprincipaladmin'})

urlpatterns = [
    path('', placeholder, name='dashboard'),
]