import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .heuristica import (
    CONTENIDO_ROSAS, CONTENIDO_GIRASOLES, CONTENIDO_LIRIOS,
    alerta_stock_flor_fecha_comercial, alerta_stock_cinta_fecha_comercial,
    alerta_stock_flor_semana_siguiente, serie_semanal_flor_completa,
    serie_semanal_flor_normal, serie_anual_evento_agregada,
    cargar_historial, cargar_stock_por_categoria,
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

        # Gráfico 1: tendencia semanal normal (sin mezclar con la predicción)
        semanal = serie_semanal_flor_completa(flor['mapeo'], historial=historial)[-SEMANAS_A_MOSTRAR:]
        labels = [f.strftime('%d %b') for f, _ in semanal]
        valores = [float(total) for _, total in semanal]

        alerta_semanal = alerta_stock_flor_semana_siguiente(
            flor['clave'], historial=historial, stock_por_categoria=stock_por_categoria,
        )
        if alerta_semanal and alerta_semanal.get('necesidad') is not None:
            labels.append('Próx. semana')
            valores.append(float(alerta_semanal['necesidad']))

        # Gráfico 2: historial de la fecha comercial (años reales) + predicción
        evento_labels = []
        evento_valores = []
        evento_indice_prediccion = None
        tiene_prediccion = bool(alerta and alerta.get('nivel') != 'SIN_DATOS' and alerta.get('necesidad') is not None)

        if nombre_prox:
            serie_evento = serie_anual_evento_agregada(flor['mapeo'], nombre_prox, historial=historial)
            for anio, total in serie_evento:
                evento_labels.append(str(anio))
                evento_valores.append(float(total))

            if tiene_prediccion:
                ultimo_anio = serie_evento[-1][0] if serie_evento else fecha_prox.year - 1
                evento_labels.append(f"{ultimo_anio + 1} (est.)")
                evento_valores.append(float(alerta['necesidad']))
                evento_indice_prediccion = len(evento_valores) - 1

        secciones.append({
            'clave': flor['clave'],
            'nombre_display': flor['nombre_display'],
            'chart_labels': json.dumps(labels),
            'chart_valores': json.dumps(valores),
            'evento_labels': json.dumps(evento_labels),
            'evento_valores': json.dumps(evento_valores),
            'evento_indice_prediccion': evento_indice_prediccion,
            'tiene_evento': bool(evento_labels),
            'alerta': alerta,
            'alerta_semanal': alerta_semanal,
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