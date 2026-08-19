from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from inventario.models import ItemInventario
from catalogo.models import Producto
from .heuristica import evaluar_alerta
from .fechas_comerciales import proxima_fecha_comercial
from .holt import serie_anual_evento, holt_pronostico

PRODUCTOS_ASISTENTE = [
    {'clave': 'rosas unidad', 'nombre_display': 'Rosas', 'categoria_inventario': 'Rosas'},
    {'clave': 'unidad girasol', 'nombre_display': 'Girasoles', 'categoria_inventario': 'Girasoles'},
    {'clave': 'ramo de 7 rosas', 'nombre_display': 'Ramo de 7 Rosas', 'producto_catalogo': 'Ramo de 7 Rosas'},
]


def obtener_stock_actual(config):
    if 'categoria_inventario' in config:
        total = ItemInventario.objects.filter(
            categoria__nombre=config['categoria_inventario']
        ).aggregate(t=Sum('stock_actual'))['t']
        return float(total or 0)

    producto = Producto.objects.filter(nombre__iexact=config['producto_catalogo']).first()
    return float(producto.unidades_listas) if producto else 0


@login_required
def dashboard(request):
    fecha_prox, nombre_prox = proxima_fecha_comercial()

    secciones = []
    for config in PRODUCTOS_ASISTENTE:
        producto = config['clave']
        stock_actual = obtener_stock_actual(config)

        serie = serie_anual_evento(producto, nombre_prox) if nombre_prox else []
        anios_data = [{'anio': anio, 'unidades': float(total)} for anio, total in serie]

        prediccion = None
        if len(serie) >= 2:
            valores = [total for _, total in serie]
            resultado_holt = holt_pronostico(valores)
            prediccion = {
                'anio': serie[-1][0] + 1,
                'unidades': float(resultado_holt['pronostico']),
                'metodo': 'Holt' if not resultado_holt['degradado_a_lineal'] else 'Holt (lineal, N=2)',
            }
        elif len(serie) == 1:
            prediccion = {
                'anio': serie[0][0] + 1,
                'unidades': float(serie[0][1]),
                'metodo': 'Sin tendencia (1 año)',
            }

        alerta = evaluar_alerta(producto, stock_actual=stock_actual)

        max_valor = max(
            [a['unidades'] for a in anios_data] + ([prediccion['unidades']] if prediccion else []) + [1]
        )

        secciones.append({
            'nombre_display': config['nombre_display'],
            'anios': anios_data,
            'prediccion': prediccion,
            'max_valor': max_valor,
            'alerta': alerta,
            'stock_actual': stock_actual,
        })

    context = {
        'secciones': secciones,
        'fecha_proxima': fecha_prox,
        'nombre_fecha_proxima': nombre_prox,
    }
    return render(request, 'asistente_ia/dashboard.html', context)