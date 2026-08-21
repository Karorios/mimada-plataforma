import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .heuristica import (
    CONTENIDO_ROSAS, CONTENIDO_GIRASOLES, CONTENIDO_LIRIOS,
    alerta_stock_flor_fecha_comercial, alerta_stock_cinta_fecha_comercial,
    serie_semanal_flor_normal, cargar_historial, cargar_stock_por_categoria,
)
from .fechas_comerciales import proxima_fecha_comercial

FLORES = [
    {'clave': 'rosas', 'nombre_display': 'Rosas', 'mapeo': CONTENIDO_ROSAS},
    {'clave': 'girasoles', 'nombre_display': 'Girasoles', 'mapeo': CONTENIDO_GIRASOLES},
    {'clave': 'lirios', 'nombre_display': 'Lirios', 'mapeo': CONTENIDO_LIRIOS},
]

SEMANAS_A_MOSTRAR = 8


@login_required
def dashboard(request):
    fecha_prox, nombre_prox = proxima_fecha_comercial()

    # Se cargan UNA sola vez y se reutilizan en todas las llamadas de abajo,
    # en vez de que cada función vuelva a consultar la base por su cuenta.
    historial = cargar_historial()
    stock_por_categoria = cargar_stock_por_categoria()

    secciones = []
    for flor in FLORES:
        alerta = None
        if nombre_prox:
            alerta = alerta_stock_flor_fecha_comercial(
                flor['clave'], nombre_prox,
                historial=historial, stock_por_categoria=stock_por_categoria,
            )

        semanal = serie_semanal_flor_normal(flor['mapeo'], historial=historial)[-SEMANAS_A_MOSTRAR:]
        labels = [f.strftime('%d %b') for f, _ in semanal]
        valores = [float(total) for _, total in semanal]

        tiene_prediccion = bool(alerta and alerta.get('nivel') != 'SIN_DATOS' and alerta.get('necesidad') is not None)
        if tiene_prediccion:
            labels.append(nombre_prox)
            valores.append(float(alerta['necesidad']))

        secciones.append({
            'clave': flor['clave'],
            'nombre_display': flor['nombre_display'],
            'chart_labels': json.dumps(labels),
            'chart_valores': json.dumps(valores),
            'indice_prediccion': len(valores) - 1 if tiene_prediccion else None,
            'alerta': alerta,
        })

    cinta = None
    if nombre_prox:
        cinta = alerta_stock_cinta_fecha_comercial(
            nombre_prox, historial=historial, stock_por_categoria=stock_por_categoria,
        )

    context = {
        'secciones': secciones,
        'cinta': cinta,
        'fecha_proxima': fecha_prox,
        'nombre_fecha_proxima': nombre_prox,
    }
    return render(request, 'asistente_ia/dashboard.html', context)