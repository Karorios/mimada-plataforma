from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from pedidos.models import Pedido, DetallePedido
from asistente_ia.models import HistorialVentas
from asistente_ia.fechas_comerciales import detectar_fecha_comercial

from .forms import VentaPresencialForm

Usuario = get_user_model()
USERNAME_MOSTRADOR = 'mostrador'


ESTADO_TABS = [
    ('TODOS', 'Todos'),
    ('PENDIENTE', 'Pendientes'),
    ('EN_PROCESO', 'En Proceso'),
    ('LISTO', 'Listos'),
    ('ENTREGADO', 'Entregados'),
    ('CANCELADO', 'Cancelados'),
]


def _construir_contexto_lista(request):
    """Arma el contexto base del listado (filtros, paginación, detalle) —
    compartido entre lista_pedidos y registrar_venta_presencial, para que
    esta última pueda re-renderizar la misma lista si el formulario falla."""
    pedidos = Pedido.objects.select_related('cliente').prefetch_related('detalles__producto')

    tab_activo = request.GET.get('tab', 'TODOS')
    if tab_activo != 'TODOS':
        pedidos = pedidos.filter(estado=tab_activo)

    query = request.GET.get('q')
    if query:
        pedidos = pedidos.filter(
            Q(cliente__first_name__icontains=query) |
            Q(cliente__email__icontains=query) |
            Q(nombre_destinatario__icontains=query) |
            Q(id__icontains=query)
        )

    pedidos = pedidos.order_by('-fecha_creacion')

    paginator = Paginator(pedidos, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    pedido_detalle = None
    ver_id = request.GET.get('ver')
    if ver_id:
        pedido_detalle = get_object_or_404(
            Pedido.objects.select_related('cliente').prefetch_related(
                'detalles__producto', 'detalles__configuracion'
            ),
            pk=ver_id
        )

    return {
        'page_obj': page_obj,
        'tabs': ESTADO_TABS,
        'tab_activo': tab_activo,
        'query': query or '',
        'total_pedidos': paginator.count,
        'pedido_detalle': pedido_detalle,
    }


@login_required
def lista_pedidos(request):
    context = _construir_contexto_lista(request)
    context['mostrar_form_presencial'] = request.GET.get('nueva') == '1'
    context['form_presencial'] = VentaPresencialForm()
    return render(request, 'pedidosadmin/lista.html', context)


@login_required
def accion_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        transiciones = {
            'aprobar': 'EN_PROCESO',
            'marcar_listo': 'LISTO',
            'entregar': 'ENTREGADO',
            'cancelar': 'CANCELADO',
        }
        if accion in transiciones:
            pedido.estado = transiciones[accion]
            pedido.save()
            messages.success(request, f'Pedido #{pedido.id} actualizado.')

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
    return redirect('pedidosadmin:dashboard')


# Se mantiene por si acaso, como página completa alternativa
@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.select_related('cliente').prefetch_related(
            'detalles__producto', 'detalles__configuracion'
        ),
        pk=pk
    )
    return render(request, 'pedidosadmin/detalle.html', {'pedido': pedido})


def obtener_cliente_mostrador():
    """Cuenta genérica usada para TODAS las ventas presenciales, para no
    tener que crear una cuenta real por cada cliente de mostrador."""
    cliente, _creado = Usuario.objects.get_or_create(
        username=USERNAME_MOSTRADOR,
        defaults={
            'email': 'mostrador@mimada.local',
            'first_name': 'Venta',
            'last_name': 'Mostrador',
            'es_cliente': False,
        },
    )
    return cliente


def inicio_semana(fecha):
    """Devuelve el sábado (fecha_inicio) de la semana a la que pertenece
    `fecha`, consistente con cómo están armadas las semanas en
    HistorialVentas (sábado a sábado)."""
    dias_desde_sabado = (fecha.weekday() - 5) % 7
    return fecha - timedelta(days=dias_desde_sabado)


def registrar_en_historial(nombre_producto, cantidad, fecha_venta):
    """Suma esta venta a la semana correspondiente de HistorialVentas,
    para que el Asistente IA la vea en la próxima predicción."""
    fecha_inicio = inicio_semana(fecha_venta)
    fecha_fin = fecha_inicio + timedelta(days=7)
    fecha_comercial = detectar_fecha_comercial(fecha_inicio, fecha_fin)

    registro, creado = HistorialVentas.objects.get_or_create(
        producto=nombre_producto,
        fecha_inicio=fecha_inicio,
        defaults={
            'fecha_fin': fecha_fin,
            'cantidad': cantidad,
            'fecha_comercial': fecha_comercial,
        },
    )
    if not creado:
        registro.cantidad += cantidad
        if not registro.fecha_comercial and fecha_comercial:
            registro.fecha_comercial = fecha_comercial
        registro.save()

    return registro


@login_required
def registrar_venta_presencial(request):
    """Procesa el formulario del panel de 'Venta de vitrina'. Si es válido,
    crea el Pedido + DetallePedido y suma a HistorialVentas, y redirige de
    vuelta a la lista. Si NO es válido, vuelve a mostrar la lista con el
    panel abierto y los errores visibles, en vez de una página aparte."""
    if request.method != 'POST':
        return redirect('pedidosadmin:dashboard')

    form = VentaPresencialForm(request.POST)
    if form.is_valid():
        datos = form.cleaned_data
        producto = datos.get('producto')
        cantidad = datos['cantidad']
        precio_unitario = datos['precio_unitario']
        subtotal = precio_unitario * cantidad

        cliente_mostrador = obtener_cliente_mostrador()

        pedido = Pedido.objects.create(
            cliente=cliente_mostrador,
            estado='ENTREGADO',
            tipo_entrega='MOSTRADOR',
            total=subtotal,
            nombre_destinatario=datos.get('nombre_cliente', ''),
            telefono_destinatario=datos.get('telefono_cliente', ''),
            fecha_entrega=datos['fecha_venta'],
        )
        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
        )

        nombre_historial = form.nombre_para_historial()
        registrar_en_historial(nombre_historial, cantidad, datos['fecha_venta'])

        messages.success(
            request,
            f'Venta de vitrina registrada (Pedido #{pedido.id}) y sumada al historial del Asistente IA.',
        )
        next_url = request.POST.get('next') or 'pedidosadmin:dashboard'
        if next_url.startswith('?'):
            return redirect(f"/pedidosadmin/{next_url}")
        return redirect(next_url)

    # formulario inválido: reconstruimos la lista y mostramos el panel con errores
    context = _construir_contexto_lista(request)
    context['mostrar_form_presencial'] = True
    context['form_presencial'] = form
    return render(request, 'pedidosadmin/lista.html', context)


def reverse_lista(request):
    from django.urls import reverse
    return reverse('pedidosadmin:dashboard')