from django.shortcuts import render
from inventario.models import ItemInventario, CategoriaInventario


def inicio(request):
    return render(request, 'pedidos/inicio.html')


def crear_detalle(request):
    def items_de(nombre_categoria):
        try:
            cat = CategoriaInventario.objects.get(nombre=nombre_categoria)
            return ItemInventario.objects.filter(categoria=cat)
        except CategoriaInventario.DoesNotExist:
            return ItemInventario.objects.none()

    rosas = items_de('Rosas')
    cintas = items_de('Cintas')
    papeles = items_de('papel coreano')
    adicionales = items_de('adicciones')

    precio_base_rosa = rosas.first().precio if rosas.exists() else 0

    return render(request, 'pedidos/crear_detalle.html', {
        'rosas': rosas,
        'cintas': cintas,
        'papeles': papeles,
        'adicionales': adicionales,
        'precio_base_rosa': precio_base_rosa,
    })