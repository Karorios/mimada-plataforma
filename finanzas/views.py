from django.shortcuts import render

# Create your views here.
def dashboard_view(request):
    clientes = [
        {
            'nombre': 'Camila Restrepo',
            'iniciales': None,
            'foto': True,
            'estado': 'VENCIDO',
            'detalle': 'Ramo Rosas + Chocolates',
            'valor_total': 245000,
            'abonado': 100000,
            'saldo': 145000,
            'fecha_info': 'Venció el 12 de Octubre, 2025',
        },
        {
            'nombre': 'Mariana Gómez',
            'iniciales': 'MG',
            'foto': False,
            'estado': 'PROXIMO',
            'detalle': 'Arreglo Floral + Orquídeas',
            'valor_total': 180000,
            'abonado': 150000,
            'saldo': 30000,
            'fecha_info': 'Vence en 2 días (15 Oct)',
        },
        {
            'nombre': 'Sofía Arango',
            'iniciales': None,
            'foto': True,
            'estado': 'AL_DIA',
            'detalle': 'Caja Lup "Eternidad"',
            'valor_total': 420000,
            'abonado': 200000,
            'saldo': 220000,
            'fecha_info': 'Próximo pago: 30 de Octubre',
        },
    ]

    total_por_cobrar = sum(c['saldo'] for c in clientes)
    clientes_con_deuda = len(clientes)
    pagos_del_mes = sum(c['abonado'] for c in clientes)

    context = {
        'clientes': clientes,
        'total_por_cobrar': total_por_cobrar,
        'clientes_con_deuda': clientes_con_deuda,
        'pagos_del_mes': pagos_del_mes,
    }
    return render(request, 'finanzas/dashboard.html', context)