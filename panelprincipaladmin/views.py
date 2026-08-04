from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from catalogo.models import Producto


@login_required(login_url='usuarios:login')
def dashboard(request):
    if not request.user.es_admin:
        raise PermissionDenied

    productos = Producto.objects.all().order_by('-fecha_creacion')

    return render(
        request,
        'panelprincipaladmin/dashboard.html',
        {
            'productos': productos
        }
    )