from django.shortcuts import render, redirect, get_object_or_404
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

    cintas = items_de('Cintas')
    papeles = items_de('papel coreano')
    adicionales = items_de('adicciones')
    peluches = items_de('Peluches')

    detalle_inicial = request.session.get('detalle_personalizado')

    return render(request, 'catalogo/inicio.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'cintas': cintas,
        'papeles': papeles,
        'adicionales': adicionales,
        'peluches': peluches,
        'detalle_inicial': detalle_inicial,
    })

def lista_productos(request):
        productos = Producto.objects.all()
        categorias = Categoria.objects.all()
        return render(request, 'catalogo/lista.html', {
            'productos': productos,
            'categorias': categorias,
        })

def detalle_producto(request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        return render(request, 'catalogo/detalle_producto.html', {
            'producto': producto,
        })

@login_required(login_url='usuarios:login')
def crear_producto(request):

    if not request.user.es_admin:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Producto creado correctamente.')
            return redirect('catalogo:admin_dashboard')
    else:
        form = ProductoForm()

    return render(request, 'catalogo/crear_producto.html', {'form': form})

@login_required(login_url='usuarios:login')
def eliminar_producto(request, pk):
    if not request.user.es_admin:
        raise PermissionDenied

    producto = Producto.objects.get(pk=pk)

    producto.delete()

    messages.success(request, "Producto eliminado correctamente.")

    return redirect('catalogo:admin_dashboard')

@login_required(login_url='usuarios:login')
def admin_dashboard(request):
    if not request.user.es_admin:
        raise PermissionDenied

    productos = Producto.objects.select_related('categoria').all()

    context = {
        'productos': productos,
        'total_productos': productos.count(),
        'productos_disponibles': productos.filter(disponible=True).count(),
        'productos_destacados': productos.filter(destacado=True).count(),
    }

    return render(request, 'catalogoadmin/dashboard.html', context)
@login_required(login_url='usuarios:login')
def editar_producto(request, pk):
    if not request.user.es_admin:
        raise PermissionDenied

    producto = Producto.objects.get(pk=pk)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('catalogo:admin_dashboard')

    else:
        form = ProductoForm(instance=producto)

    return render(
        request,
        "catalogo/crear_producto.html",
        {
            "form": form,
            "editar": True
        }
    )

@login_required
def actualizar_listas(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            nuevo_valor = int(request.POST.get('unidades_listas', 0))
            producto.unidades_listas = max(0, nuevo_valor)
            producto.save()
            messages.success(request, f'"{producto.nombre}" actualizado.')
        except (ValueError, TypeError):
            messages.error(request, 'Valor inválido.')
    return redirect('catalogo:admin_dashboard')