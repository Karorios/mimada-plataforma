from decimal import Decimal, ROUND_CEILING
from datetime import date
from django.db.models import Sum
from inventario.models import ItemInventario
from .models import HistorialVentas
from .holt import serie_anual_evento, holt_pronostico
from django.db.models import Q

# ---------------------------------------------------------------------------
# Mapeo: cuántas unidades de cada flor trae un producto vendido.
# Se usa para agrupar el consumo real de flores, sin importar si se vendió
# como unidad suelta o dentro de un ramo/combo.
# ---------------------------------------------------------------------------

CONTENIDO_ROSAS = {
    'rosas unidad': 1, 'rosas unidad decoradas': 1, 'ramo de tres rosas': 3,
    'ramo de 4 rosas': 4, 'ramo peluche mediano y 4 rosas': 4,
    'ramo 6 rosas y dulces esfera': 6, 'ramo 6 rosas y peluche esfera': 6,
    'lotso pequeño y 6 rosas': 6, 'ramo de 7 rosas': 7, 'ramo con 20 rosas': 20,
    'ramo de peluche mediano y 20 rosas': 20, 'ramo peluche grande y 20 rosas': 20,
    'ramo de 7 girasoles, 6 rosas y 6 plumerias': 6,
    'ramo de 7 con nutella': 7,
    'ramo con espejo': 9,
    'ramo con chocolates corazon': 7,
    'ramo 7 flores y llavero': 7,
    'ramo de 6 flores y peluche': 6,
    'cajita hombre reloj': 1,
    'cajita hombre manilla': 1,
}

CONTENIDO_GIRASOLES = {
    'unidad girasol': 1,
    'ramo de 7 girasoles, 6 rosas y 6 plumerias': 7,
}

CONTENIDO_LIRIOS = {
    'ramo de 6 lirios': 6,
}

# Nombre de la categoría en ItemInventario para cada flor (para sumar el stock)
CATEGORIA_INVENTARIO_POR_FLOR = {
    'rosas': 'Rosas',
    'girasoles': 'Girasoles',
    'lirios': 'Lirios',
}

METROS_CINTA_POR_ROSA = Decimal('1.10')

MINIMO_SEMANAS_DEFAULT = 5

def  cargar_historial():
    """Trae TODO el historial de ventas en una sola query, como lista en
    memoria. Pásalo como `historial=` a las demás funciones para evitar que
    cada una vuelva a consultar la base por separado."""
    return list(HistorialVentas.objects.all())


def cargar_stock_por_categoria():
    """Trae el stock actual de Inventario agrupado por categoría, en una
    sola query. Devuelve un dict {nombre_categoria_lower: Decimal}."""
    filas = (
        ItemInventario.objects
        .values('categoria__nombre')
        .annotate(total=Sum('stock_actual'))
    )
    return {
        (f['categoria__nombre'] or '').lower(): (f['total'] or Decimal('0'))
        for f in filas
    }


def _obtener_historial(historial):
    return historial if historial is not None else cargar_historial()


def factor_crecimiento_otras_fechas_flor(mapeo_contenido, excluir_evento=None):
    """Promedio del crecimiento año-a-año observado en OTROS eventos
    comerciales (agregados por flor), para estimar un evento que
    todavía solo tiene 1 año de historia."""
    eventos = (
        HistorialVentas.objects
        .exclude(fecha_comercial__isnull=True)
        .exclude(fecha_comercial='')
        .values_list('fecha_comercial', flat=True)
        .distinct()
    )

    factores = []
    for evento in eventos:
        if evento == excluir_evento:
            continue
        serie = serie_anual_evento_agregada(mapeo_contenido, evento)
        if len(serie) >= 2:
            valores = [total for _, total in serie]
            if valores[0] and valores[0] != 0:
                factores.append(valores[-1] / valores[0])

    if not factores:
        return None

    promedio = sum(factores) / Decimal(len(factores))
    return max(Decimal('0.8'), min(Decimal('1.8'), promedio))


# ---------------------------------------------------------------------------
# NUEVO: consumo agregado por FLOR (rosas / girasoles / lirios), sumando
# entre todos los productos que la contienen (unidad suelta + ramos/combos).
# ---------------------------------------------------------------------------

def total_flor_por_semana(mapeo_contenido, fecha_inicio_semana):
    """Suma la cantidad total de una flor vendida en una semana específica,
    sumando entre TODOS los productos que la contienen."""
    registros = HistorialVentas.objects.filter(fecha_inicio=fecha_inicio_semana)
    total = Decimal('0')
    for r in registros:
        factor = mapeo_contenido.get(r.producto.strip().lower())
        if factor:
            total += Decimal(r.cantidad) * Decimal(factor)
    return total


def serie_semanal_flor_normal(mapeo_contenido):
    registros = (
        HistorialVentas.objects
        .filter(Q(fecha_comercial__isnull=True) | Q(fecha_comercial=''))
        .order_by('fecha_inicio')
    )
    semanas = set()
    acumulado = {}
    for r in registros:
        semanas.add(r.fecha_inicio)
        factor = mapeo_contenido.get(r.producto.strip().lower())
        if factor:
            acumulado[r.fecha_inicio] = acumulado.get(r.fecha_inicio, Decimal('0')) + Decimal(r.cantidad) * Decimal(factor)
    return [(s, acumulado.get(s, Decimal('0'))) for s in sorted(semanas)]


def serie_anual_evento_agregada(mapeo_contenido, nombre_fecha_comercial):
    """Como serie_anual_evento, pero sumando TODOS los productos que
    contienen esa flor, y usando MAX (no SUM) cuando dos fecha_inicio
    distintas caen en el mismo año para el mismo evento."""
    fechas = (
        HistorialVentas.objects
        .filter(fecha_comercial__iexact=nombre_fecha_comercial)
        .values_list('fecha_inicio', flat=True).distinct()
    )

    totales_por_año = {}
    for f in fechas:
        total_semana = total_flor_por_semana(mapeo_contenido, f)
        año = f.year
        if año not in totales_por_año or total_semana > totales_por_año[año]:
            totales_por_año[año] = total_semana

    return sorted(totales_por_año.items())


def necesidad_flor_fecha_comercial(mapeo_contenido, nombre_fecha_comercial):
    serie = serie_anual_evento_agregada(mapeo_contenido, nombre_fecha_comercial)
    valores = [total for _, total in serie]

    if len(valores) >= 2:
        resultado = holt_pronostico(valores)
        return resultado['pronostico'].to_integral_value(rounding=ROUND_CEILING)

    if len(valores) == 1:
        factor = factor_crecimiento_otras_fechas_flor(mapeo_contenido, excluir_evento=nombre_fecha_comercial)
        if factor:
            return (valores[0] * factor).to_integral_value(rounding=ROUND_CEILING)
        return valores[0].to_integral_value(rounding=ROUND_CEILING)

    return None


def alerta_stock_flor_fecha_comercial(nombre_flor, nombre_fecha_comercial, dias_entrega_proveedor=3, minimo_semanas=5):
    mapeos = {'rosas': CONTENIDO_ROSAS, 'girasoles': CONTENIDO_GIRASOLES, 'lirios': CONTENIDO_LIRIOS}
    mapeo_contenido = mapeos.get(nombre_flor)
    categoria_inventario = CATEGORIA_INVENTARIO_POR_FLOR.get(nombre_flor)

    if not mapeo_contenido or not categoria_inventario:
        return None

    if semanas_con_venta_de_flor(mapeo_contenido, minimo_semanas) < minimo_semanas:
        return {
            'nivel': 'SIN_DATOS',
            'mensaje': f"Todavía no hay suficiente historial de ventas de {nombre_flor} para hacer una predicción confiable.",
            'necesidad': None, 'stock_actual': None, 'faltante': None,
        }

    stock_actual = ItemInventario.objects.filter(
        categoria__nombre__iexact=categoria_inventario
    ).aggregate(total=Sum('stock_actual'))['total'] or Decimal('0')

    necesidad = necesidad_flor_fecha_comercial(mapeo_contenido, nombre_fecha_comercial)
    if necesidad is None:
        return None

    faltante = necesidad - stock_actual

    if faltante > 0:
        nivel = 'ALERTA'
        mensaje = (
            f"Para {nombre_fecha_comercial} vas a necesitar ~{necesidad} {nombre_flor}, "
            f"pero solo tienes {stock_actual} en inventario. Te faltan ~{faltante}. "
            f"Pide con al menos {dias_entrega_proveedor} días de anticipación."
        )
    else:
        nivel = 'OK'
        mensaje = (
            f"Para {nombre_fecha_comercial} vas a necesitar ~{necesidad} {nombre_flor}, "
            f"y tienes {stock_actual}. Vas bien."
        )

    return {
        'nivel': nivel, 'mensaje': mensaje, 'necesidad': necesidad,
        'stock_actual': stock_actual, 'faltante': max(faltante, Decimal('0')),
    }

def semanas_con_venta_de_flor(mapeo_contenido, minimo=5):
    """Cuenta en cuántas semanas distintas (de todo el historial) se vendió
    algo de esta flor, sin importar la fecha. Sirve para decidir si hay
    base suficiente para hacer cualquier tipo de proyección."""
    registros = HistorialVentas.objects.all()
    semanas = set()
    for r in registros:
        factor = mapeo_contenido.get(r.producto.strip().lower())
        if factor and r.cantidad > 0:
            semanas.add(r.fecha_inicio)
    return len(semanas)



def alerta_stock_cinta_fecha_comercial(nombre_fecha_comercial, dias_entrega_proveedor=3, minimo_semanas=5):
    """Verifica si el stock de cinta (en metros) alcanza para la cantidad
    de rosas proyectada para la próxima fecha comercial."""
    if semanas_con_venta_de_flor(CONTENIDO_ROSAS, minimo_semanas) < minimo_semanas:
        return {
            'nivel': 'SIN_DATOS',
            'mensaje': "Todavía no hay suficiente historial de ventas de rosas para proyectar el consumo de cinta.",
            'necesidad_metros': None, 'stock_actual_metros': None, 'faltante_metros': None,
        }

    necesidad_rosas = necesidad_flor_fecha_comercial(CONTENIDO_ROSAS, nombre_fecha_comercial)
    if necesidad_rosas is None:
        return None

    necesidad_metros = (necesidad_rosas * METROS_CINTA_POR_ROSA).quantize(Decimal('0.01'))

    stock_actual = ItemInventario.objects.filter(
        categoria__nombre__iexact='Cintas'
    ).aggregate(total=Sum('stock_actual'))['total'] or Decimal('0')

    faltante = necesidad_metros - stock_actual

    if faltante > 0:
        nivel = 'ALERTA'
        mensaje = (
            f"Para {nombre_fecha_comercial} vas a necesitar ~{necesidad_metros} metros de cinta "
            f"({necesidad_rosas} rosas × 1.10m), pero solo tienes {stock_actual} metros. "
            f"Te faltan ~{faltante} metros. Pide con al menos {dias_entrega_proveedor} días de anticipación."
        )
    else:
        nivel = 'OK'
        mensaje = (
            f"Para {nombre_fecha_comercial} vas a necesitar ~{necesidad_metros} metros de cinta, "
            f"y tienes {stock_actual}. Vas bien."
        )

    return {
        'nivel': nivel, 'mensaje': mensaje, 'necesidad_metros': necesidad_metros,
        'stock_actual_metros': stock_actual, 'faltante_metros': max(faltante, Decimal('0')),
    }

def resumen_rosas_y_cinta(nombre_fecha_comercial, dias_entrega_proveedor=3):
    """Junta en un solo resultado la proyección de rosas necesarias y si
    el stock de cinta alcanza para armarlas, para mostrar en el dashboard."""
    rosas = alerta_stock_flor_fecha_comercial('rosas', nombre_fecha_comercial, dias_entrega_proveedor)
    cinta = alerta_stock_cinta_fecha_comercial(nombre_fecha_comercial, dias_entrega_proveedor)

    return {
        'fecha_comercial': nombre_fecha_comercial,
        'rosas': rosas,
        'cinta': cinta,
    }