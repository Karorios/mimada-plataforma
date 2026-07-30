from django.shortcuts import render
from catalogo.models import Producto, Categoria


def inicio(request):
    productos_destacados = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'catalogo/inicio.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
    })


def lista_productos(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'catalogo/lista.html', {
        'productos': productos,
        'categorias': categorias,
    })