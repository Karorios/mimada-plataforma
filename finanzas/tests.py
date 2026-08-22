from django.test import TestCase
from django.contrib.auth import get_user_model
from pedidos.models import Pedido
from .forms import AbonoForm

Usuario = get_user_model()


class AbonoFormTest(TestCase):
    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            direccion='Calle 10A #34-21',
            total=100000,
        )

    def test_abono_valido(self):
        form = AbonoForm(data={
            'pedido': self.pedido.id,
            'monto': 50000,
            'metodo_pago': 'EFECTIVO',
            'nota': 'Primer abono',
        })
        self.assertTrue(form.is_valid())

    def test_abono_requiere_pedido(self):
        form = AbonoForm(data={
            'pedido': '',
            'monto': 50000,
            'metodo_pago': 'EFECTIVO',
        })
        self.assertFalse(form.is_valid())

    def test_abono_requiere_monto(self):
        form = AbonoForm(data={
            'pedido': self.pedido.id,
            'monto': '',
            'metodo_pago': 'EFECTIVO',
        })
        self.assertFalse(form.is_valid())

    def test_abono_nota_es_opcional(self):
        form = AbonoForm(data={
            'pedido': self.pedido.id,
            'monto': 30000,
            'metodo_pago': 'TRANSFERENCIA',
            'nota': '',
        })
        self.assertTrue(form.is_valid())