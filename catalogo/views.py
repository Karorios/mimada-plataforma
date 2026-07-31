from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Producto, Categoria
from .forms import ProductoForm


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


@login_required(login_url='usuarios:login')
def crear_producto(request):
    if not request.user.es_admin:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente. Ya está visible en el catálogo.')
            return redirect('catalogo:crear_producto')
    else:
        form = ProductoForm()

    return render(request, 'catalogo/crear_producto.html', {'form': form})