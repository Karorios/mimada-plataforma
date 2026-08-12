from django.core.exceptions import ValidationError

RANGOS_PLIEGOS = [
    (1, 1, 1),
    (2, 4, 2),
    (5, 7, 4),
    (8, 35, 6),
]


def calcular_pliegos(total_flores, pliegos_manual=None):
    """
    Devuelve cuántos pliegos de papel se deben descontar.
    - 1 a 35 flores: usa la tabla de rangos (valida stock más adelante).
    - 50 o 100 flores: usa el valor manual que indicó el cliente (no valida stock).
    - Cualquier otro total (ej. 36-49) es inválido.
    """
    if total_flores in (50, 100):
        if not pliegos_manual or pliegos_manual < 1:
            raise ValidationError("Debes indicar cuántos pliegos de papel necesitas.")
        return pliegos_manual

    for minimo, maximo, pliegos in RANGOS_PLIEGOS:
        if minimo <= total_flores <= maximo:
            return pliegos

    raise ValidationError("La cantidad de flores seleccionada no es válida.")


def es_modo_manual(total_flores):
    return total_flores in (50, 100)