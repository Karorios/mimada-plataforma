from urllib.parse import quote
from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from inventario.models import ItemInventario, CategoriaInventario
from catalogo.models import Producto

from .forms import PedidoForm
from .models import Pedido, DetallePedido


def inicio(request):
    return render(request, "pedidos/inicio.html")


def crear_detalle(request):

    def items_de(nombre_categoria):
        try:
            categoria = CategoriaInventario.objects.get(nombre=nombre_categoria)
            return ItemInventario.objects.filter(categoria=categoria)
        except CategoriaInventario.DoesNotExist:
            return ItemInventario.objects.none()

    rosas = items_de("Rosas")
    girasoles = items_de("girasoles")
    cintas = items_de("Cintas")
    papeles = items_de("papel coreano")
    adicionales = items_de("adicciones")

    return render(
        request,
        "pedidos/crear_detalle.html",
        {
            "rosas": rosas,
            "girasoles": girasoles,
            "cintas": cintas,
            "papeles": papeles,
            "adicionales": adicionales,
            "precio_base_rosa": rosas.first().precio if rosas.exists() else 0,
            "precio_base_girasol": girasoles.first().precio if girasoles.exists() else 0,
        },
    )


@login_required(login_url="usuarios:login")
def crear_pedido(request, producto_id):

    producto = get_object_or_404(Producto, pk=producto_id)

    if request.method == "POST":

        form = PedidoForm(request.POST)

        if form.is_valid():

            datos = form.cleaned_data.copy()

            # La sesión no puede guardar objetos date
            datos["fecha_entrega"] = datos["fecha_entrega"].isoformat()

            request.session["pedido"] = datos
            request.session["producto"] = producto.id

            return redirect("pedidos:resumen")

    else:
        form = PedidoForm()

    return render(
        request,
        "pedidos/crear_pedido.html",
        {
            "form": form,
            "producto": producto,
        },
    )


@login_required(login_url="usuarios:login")
def resumen(request):

    datos = request.session.get("pedido")

    if not datos:
        return redirect("pedidos:inicio")

    producto_id = request.session.get("producto")

    producto = get_object_or_404(Producto, pk=producto_id)

    return render(
        request,
        "pedidos/resumen.html",
        {
            "datos": datos,
            "producto": producto,
        },
    )


@login_required(login_url="usuarios:login")
def confirmar_pedido(request):

    datos = request.session.get("pedido")

    if not datos:
        return redirect("pedidos:inicio")

    producto_id = request.session.get("producto")

    producto = get_object_or_404(Producto, pk=producto_id)

    pedido = Pedido.objects.create(

        cliente=request.user,

        tipo_entrega=datos["tipo_entrega"],
        es_regalo=datos["es_regalo"],
        entrega_anonima=datos["entrega_anonima"],

        nombre_destinatario=datos["nombre_destinatario"],
        telefono_destinatario=datos["telefono_destinatario"],

        mensaje=datos["mensaje"],

        direccion=datos["direccion"],
        barrio=datos["barrio"],
        ciudad=datos["ciudad"],
        referencia=datos["referencia"],

        # Convertimos nuevamente el texto a fecha
        fecha_entrega=date.fromisoformat(datos["fecha_entrega"]),

        hora_entrega=datos["hora_entrega"],

        valor_domicilio=0,

        total=producto.precio,
    )

    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=1,
        precio_unitario=producto.precio,
        subtotal=producto.precio,
    )

    mensaje = f"""
🌸 *Nuevo pedido Mimada*

Pedido No: {pedido.id}

Producto:
{producto.nombre}

Valor:
${producto.precio}

Tipo de entrega:
{pedido.get_tipo_entrega_display()}

Dirección:
{pedido.direccion}

Barrio:
{pedido.barrio}

Ciudad:
{pedido.ciudad}

Fecha:
{pedido.fecha_entrega}

Hora:
{pedido.hora_entrega}

¿Es regalo?
{'Sí' if pedido.es_regalo else 'No'}

Destinatario:
{pedido.nombre_destinatario}

Teléfono:
{pedido.telefono_destinatario}

Mensaje:
{pedido.mensaje}

Muchas gracias.

Quedo atento(a) a la información para realizar el pago.
"""

    telefono = "573238883587"

    url = f"https://wa.me/{telefono}?text={quote(mensaje)}"

    request.session.pop("pedido", None)
    request.session.pop("producto", None)

    return redirect(url)