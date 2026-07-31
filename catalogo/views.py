from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Producto, Categoria
from .forms import ProductoForm
from inventario.models import ItemInventario, CategoriaInventario


def inicio(request):
    productos_destacados = Producto.objects.all()
    categorias = Categoria.objects.all()

    def items_de(nombre_categoria):
        try:
            cat = CategoriaInventario.objects.get(nombre=nombre_categoria)
            return ItemInventario.objects.filter(categoria=cat)
        except CategoriaInventario.DoesNotExist:
            return ItemInventario.objects.none()

    rosas = items_de('Rosas')
    girasoles = items_de('girasoles')
    cintas = items_de('Cintas')
    papeles = items_de('papel coreano')
    adicionales = items_de('adicciones')

    precio_base_rosa = rosas.first().precio if rosas.exists() else None
    precio_base_girasol = girasoles.first().precio if girasoles.exists() else None

    return render(request, 'catalogo/inicio.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'rosas': rosas,
        'girasoles': girasoles,
        'cintas': cintas,
        'papeles': papeles,
        'adicionales': adicionales,
        'precio_base_rosa': precio_base_rosa,
        'precio_base_girasol': precio_base_girasol,
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