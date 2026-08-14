import openpyxl
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from asistente_ia.fechas_comerciales import detectar_fecha_comercial


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
    for year in (fecha_inicio.year, fecha_fin.year):
        for fecha, nombre in fechas_comerciales(year).items():
            if fecha_inicio <= fecha <= fecha_fin:
                return nombre
    return None


class Command(BaseCommand):
    help = 'Importa el historial de ventas desde el Excel (Hoja 2, formato ancho)'

    def add_arguments(self, parser):
        parser.add_argument('ruta_excel', type=str)

    def handle(self, *args, **options):
        ruta = options['ruta_excel']
        wb = openpyxl.load_workbook(ruta, data_only=True)
        ws = wb['Hoja 2']

        filas = list(ws.iter_rows(values_only=True))
        encabezados = filas[1]  # fila 2 tiene los nombres de columna
        productos_cols = {
            idx: nombre for idx, nombre in enumerate(encabezados)
            if idx >= 5 and nombre  # columnas de producto empiezan en la F (índice 5)
        }

        creados = 0
        HistorialVentas.objects.all().delete()  # limpia antes de reimportar, evita duplicados

        for fila in filas[2:]:
            fecha_inicio = fila[2]
            fecha_fin = fila[3]
            if not fecha_inicio or not fecha_fin:
                continue

            fecha_inicio = fecha_inicio.date() if hasattr(fecha_inicio, 'date') else fecha_inicio
            fecha_fin = fecha_fin.date() if hasattr(fecha_fin, 'date') else fecha_fin

            comercial = detectar_fecha_comercial(fecha_inicio, fecha_fin)

            for idx, producto in productos_cols.items():
                cantidad = fila[idx] if idx < len(fila) else None
                cantidad = cantidad if cantidad else 0
                if cantidad == 0:
                    continue  # no guardamos ceros, para no llenar la tabla de basura

                HistorialVentas.objects.create(
                    producto=producto.strip(),
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    cantidad=int(cantidad),
                    fecha_comercial=comercial,
                )
                creados += 1

        self.stdout.write(self.style.SUCCESS(f"Se importaron {creados} registros de ventas."))