from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from pedidos.models import Pedido


ESTADO_TABS = [
    ('TODOS', 'Todos'),
    ('PENDIENTE', 'Pendientes'),
    ('EN_PROCESO', 'En Proceso'),
    ('LISTO', 'Listos'),
    ('ENTREGADO', 'Entregados'),
    ('CANCELADO', 'Cancelados'),
]


@login_required
def lista_pedidos(request):
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

    context = {
        'page_obj': page_obj,
        'tabs': ESTADO_TABS,
        'tab_activo': tab_activo,
        'query': query or '',
        'total_pedidos': paginator.count,
        'pedido_detalle': pedido_detalle,
    }
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