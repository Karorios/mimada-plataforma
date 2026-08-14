from datetime import timedelta
from django.db.models import F
from .models import HistorialVentas
from .fechas_comerciales import detectar_fecha_comercial


def inicio_de_semana(fecha):
    """Lunes de la semana que contiene esa fecha."""
    return fecha - timedelta(days=fecha.weekday())


def registrar_venta(producto, cantidad, fecha):
    if cantidad <= 0:
        return

    fecha_inicio = inicio_de_semana(fecha)
    fecha_fin = fecha_inicio + timedelta(days=6)
    comercial = detectar_fecha_comercial(fecha_inicio, fecha_fin)

    registro, creado = HistorialVentas.objects.get_or_create(
        producto=producto,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        defaults={'cantidad': cantidad, 'fecha_comercial': comercial}
    )
    if not creado:
        HistorialVentas.objects.filter(pk=registro.pk).update(cantidad=F('cantidad') + cantidad)