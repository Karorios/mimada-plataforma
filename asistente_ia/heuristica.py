from decimal import Decimal
from datetime import date
from django.db.models import Sum
from .models import HistorialVentas
from .fechas_comerciales import proxima_fecha_comercial
from .holt import serie_anual_evento, holt_pronostico


def consumo_promedio_semanal(producto, semanas=8):
    """Promedio de unidades vendidas por semana, de las últimas N semanas con datos."""
    registros = HistorialVentas.objects.filter(
        producto__iexact=producto
    ).order_by('-fecha_inicio')[:semanas]

    if not registros:
        return Decimal('0')

    total = sum(r.cantidad for r in registros)
    return Decimal(total) / Decimal(len(registros))


def consumo_promedio_diario(producto, semanas=8):
    """El promedio semanal dividido en 7, para usarlo en el punto de reorden."""
    return consumo_promedio_semanal(producto, semanas) / Decimal('7')


PRODUCTOS_CON_HOLT = ['rosas unidad', 'unidad girasol', 'ramo de 7 rosas']


def proyeccion_fecha_comercial(producto, nombre_fecha_comercial, fecha_referencia=None):
    """
    Solo los 3 productos más vendidos (PRODUCTOS_CON_HOLT) reciben ajuste estacional
    con el método de Holt. El resto de productos no se ajusta por fecha comercial,
    usan su cálculo normal de consumo todo el año.
    """
    if producto.lower() not in PRODUCTOS_CON_HOLT:
        return None
    serie = serie_anual_evento(producto, nombre_fecha_comercial)
    valores = serie_anual_evento(producto, nombre_fecha_comercial)

    if len(valores) >= 2:
        resultado = holt_pronostico(valores)
        return {
            'base_historica': valores[-1],
            'proyeccion': resultado['pronostico'],
            'metodo': 'Holt (degradado a lineal, N=2)' if resultado['degradado_a_lineal'] else 'Holt',
            'nivel': resultado['nivel'],
            'tendencia': resultado['tendencia'],
        }

    if len(valores) == 1:
        return {
            'base_historica': valores[0],
            'proyeccion': valores[0],
            'metodo': 'Sin tendencia (solo 1 año de historia)',
            'nivel': valores[0],
            'tendencia': Decimal('0'),
        }

    return None


def punto_reorden(producto, dias_entrega_proveedor=3, stock_seguridad_dias=3, fecha_referencia=None):
    consumo_diario = consumo_promedio_diario(producto)

    fecha_proxima, nombre_proxima = proxima_fecha_comercial(desde=fecha_referencia)
    hoy = fecha_referencia or date.today()
    dias_para_fecha = (fecha_proxima - hoy).days if fecha_proxima else None

    ajuste_estacional = False
    proyeccion_info = None
    if dias_para_fecha is not None and dias_para_fecha <= 21:
        proyeccion_info = proyeccion_fecha_comercial(producto, nombre_proxima, fecha_referencia)
        if proyeccion_info:
            consumo_diario = proyeccion_info['proyeccion'] / Decimal('7')
            ajuste_estacional = True

    stock_seguridad = consumo_diario * Decimal(stock_seguridad_dias)
    if ajuste_estacional:
        stock_seguridad *= Decimal('1.5')

    reorden = (consumo_diario * Decimal(dias_entrega_proveedor)) + stock_seguridad

    return {
        'punto_reorden': round(reorden, 2),
        'consumo_diario_usado': round(consumo_diario, 2),
        'ajuste_estacional_aplicado': ajuste_estacional,
        'fecha_comercial_proxima': nombre_proxima,
        'dias_para_fecha_comercial': dias_para_fecha,
        'proyeccion': proyeccion_info,
    }


def evaluar_alerta(producto, stock_actual, dias_entrega_proveedor=3, fecha_referencia=None):
    resultado = punto_reorden(producto, dias_entrega_proveedor, fecha_referencia=fecha_referencia)
    reorden = resultado['punto_reorden']

    if stock_actual <= 0:
        nivel = 'CRITICO'
        mensaje = f"{producto}: sin stock (0 unidades)."
    elif stock_actual <= reorden:
        nivel = 'ALERTA'
        mensaje = f"{producto}: stock bajo ({stock_actual}), por debajo del punto de reorden ({reorden})."
    else:
        nivel = 'OK'
        mensaje = f"{producto}: stock suficiente ({stock_actual})."

    if resultado['ajuste_estacional_aplicado'] and resultado['proyeccion']:
        p = resultado['proyeccion']
        mensaje += (
            f" Se acerca {resultado['fecha_comercial_proxima']} en {resultado['dias_para_fecha_comercial']} días. "
            f"Proyección (método {p['metodo']}): ~{p['proyeccion']} unidades "
            f"(último año vendiste {p['base_historica']})."
        )

    return {'nivel': nivel, 'mensaje': mensaje, **resultado}