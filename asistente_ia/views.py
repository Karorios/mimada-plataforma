from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from inventario.models import ItemInventario
from catalogo.models import Producto
from .heuristica import evaluar_alerta
from .fechas_comerciales import proxima_fecha_comercial

ORDEN_NIVEL = {'CRITICO': 0, 'ALERTA': 1, 'OK': 2}


@login_required
def dashboard(request):
    alertas = []

    if ItemInventario.objects.filter(categoria__nombre='Rosas').exists():
        stock_rosas = ItemInventario.objects.filter(
            categoria__nombre='Rosas'
        ).aggregate(total=Sum('stock_actual'))['total'] or 0
        alertas.append(evaluar_alerta('rosas unidad', stock_actual=float(stock_rosas)))

    if ItemInventario.objects.filter(categoria__nombre='Girasoles').exists():
        stock_girasoles = ItemInventario.objects.filter(
            categoria__nombre='Girasoles'
        ).aggregate(total=Sum('stock_actual'))['total'] or 0
        alertas.append(evaluar_alerta('unidad girasol', stock_actual=float(stock_girasoles)))

    for producto in Producto.objects.filter(disponible=True):
        alertas.append(evaluar_alerta(producto.nombre.lower(), stock_actual=producto.unidades_listas))

    alertas.sort(key=lambda a: ORDEN_NIVEL.get(a['nivel'], 3))

    fecha_prox, nombre_prox = proxima_fecha_comercial()

    context = {
        'alertas': alertas,
        'fecha_proxima': fecha_prox,
        'nombre_fecha_proxima': nombre_prox,
    }
    return render(request, 'asistente_ia/dashboard.html', context)