from datetime import date, timedelta


def segundo_domingo_mayo(year):
    d = date(year, 5, 1)
    domingos = 0
    while True:
        if d.weekday() == 6:
            domingos += 1
            if domingos == 2:
                return d
        d += timedelta(days=1)


def tercer_sabado_septiembre(year):
    d = date(year, 9, 1)
    sabados = 0
    while True:
        if d.weekday() == 5:
            sabados += 1
            if sabados == 3:
                return d
        d += timedelta(days=1)


def fechas_comerciales(year):
    return {
        date(year, 2, 14): "San Valentín",
        date(year, 3, 8): "Día de la Mujer",
        segundo_domingo_mayo(year): "Día de la Madre",
        tercer_sabado_septiembre(year): "Día del Amor y la Amistad",
        date(year, 10, 31): "Halloween",
        date(year, 12, 7): "Día de las Velitas",
        date(year, 12, 24): "Navidad",
    }


def detectar_fecha_comercial(fecha_inicio, fecha_fin):
    """Dado un rango de fechas, dice si coincide con alguna fecha comercial.
    Si la fecha cae justo en el límite entre 2 semanas, se prioriza la semana
    que YA VENÍA CORRIENDO (fecha_inicio antes de la fecha comercial), no la
    que apenas empieza ese mismo día."""
    for year in (fecha_inicio.year, fecha_fin.year):
        for fecha, nombre in fechas_comerciales(year).items():
            if fecha_inicio <= fecha <= fecha_fin:  # antes: fecha_inicio <= fecha <= fecha_fin
                return nombre
    return None


def proxima_fecha_comercial(desde=None):
    """Devuelve (fecha, nombre) de la siguiente fecha comercial a partir de hoy."""
    if desde is None:
        desde = date.today()

    candidatas = []
    for year in (desde.year, desde.year + 1):
        candidatas.extend(fechas_comerciales(year).items())

    futuras = [(f, n) for f, n in candidatas if f >= desde]
    futuras.sort(key=lambda x: x[0])
    return futuras[0] if futuras else (None, None)