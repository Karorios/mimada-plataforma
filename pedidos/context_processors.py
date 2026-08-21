from .carrito import cantidad_total


def carrito(request):
    return {"carrito_cantidad": cantidad_total(request)}