from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Avg
from .models import HistorialVentas
from .fechas_comerciales import proxima_fecha_comercial


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


def consumo_historico_en_fecha_comercial(producto, nombre_fecha_comercial):
    """Cuánto se ha vendido en promedio de este producto, específicamente
    en semanas que coincidieron con esta fecha comercial en años anteriores."""
    registros = HistorialVentas.objects.filter(
        producto__iexact=producto,
        fecha_comercial=nombre_fecha_comercial
    )
    if not registros.exists():
        return None
    return registros.aggregate(promedio=Avg('cantidad'))['promedio']

def promedio_mismo_periodo_año_anterior(producto, semanas=8, fecha_referencia=None):
    """Promedio semanal de este producto, hace un año, en el mismo periodo del calendario."""
    hoy = fecha_referencia or date.today()
    fecha_fin_periodo = hoy - timedelta(days=365)
    fecha_inicio_periodo = fecha_fin_periodo - timedelta(weeks=semanas)

    registros = HistorialVentas.objects.filter(
        producto__iexact=producto,
        fecha_inicio__gte=fecha_inicio_periodo,
        fecha_inicio__lte=fecha_fin_periodo,
    )
    if not registros.exists():
        return None

    total = registros.aggregate(t=Sum('cantidad'))['t']
    semanas_con_datos = registros.count()
    return Decimal(total) / Decimal(semanas_con_datos) if semanas_con_datos else None


def factor_tendencia(producto, semanas=8, fecha_referencia=None):
    """>1 significa que estás vendiendo más que en la misma época del año pasado.
    <1 significa que estás vendiendo menos. Se limita entre 0.5x y 2.0x para
    evitar proyecciones descabelladas si hay muy pocos datos."""
    reciente = consumo_promedio_semanal(producto, semanas)
    anterior = promedio_mismo_periodo_año_anterior(producto, semanas, fecha_referencia)

    if not anterior or anterior == 0:
        return Decimal('1')  # sin suficiente historia para comparar, no ajusta

    factor = reciente / anterior
    return max(Decimal('0.5'), min(Decimal('2.0'), factor))


def proyeccion_fecha_comercial(producto, nombre_fecha_comercial, fecha_referencia=None):
    """Proyección estimada de unidades para la próxima fecha comercial,
    ajustando lo que vendiste el año pasado según tu tendencia reciente."""
    base = consumo_historico_en_fecha_comercial(producto, nombre_fecha_comercial)
    if base is None:
        return None

    factor = factor_tendencia(producto, fecha_referencia=fecha_referencia)
    proyeccion = Decimal(base) * factor

    return {
        'base_historica': round(Decimal(base), 2),
        'factor_tendencia': round(factor, 2),
        'proyeccion': round(proyeccion, 2),
    }

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
        tendencia_txt = "más" if p['factor_tendencia'] > 1 else ("menos" if p['factor_tendencia'] < 1 else "igual")
        mensaje += (
            f" Se acerca {resultado['fecha_comercial_proxima']} en {resultado['dias_para_fecha_comercial']} días. "
            f"Proyección: ~{p['proyeccion']} unidades (el año pasado vendiste {p['base_historica']}, "
            f"y ahora estás vendiendo {tendencia_txt} que en esa misma época del año pasado)."
        )

    return {'nivel': nivel, 'mensaje': mensaje, **resultado}