from django import template

register = template.Library()


@register.filter
def formato_pesos(valor):

    try:
        numero = int(round(float(valor)))
    except (TypeError, ValueError):
        return valor

    texto = f"{numero:,}"
    return texto.replace(",", ".")
