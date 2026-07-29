from django.shortcuts import render
from catalogo.models import Producto


def inicio(request):
    productos_destacados = Producto.objects.filter(
        destacado=True,
        disponible=True
    )
    return render(request, 'catalogo/inicio.html', {
        'productos_destacados': productos_destacados,
    })