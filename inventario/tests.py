from django.test import TestCase
from .forms import ItemInventarioForm, CategoriaInventarioForm
from .models import CategoriaInventario


class ItemInventarioFormTest(TestCase):
    def setUp(self):
        self.categoria = CategoriaInventario.objects.create(nombre='Rosas', tipo='PRODUCTO_TERMINADO')

    def test_item_valido(self):
        form = ItemInventarioForm(data={
            'categoria': self.categoria.id,
            'nombre': 'Rosa Roja',
            'unidad_medida': 'UNIDAD',
            'stock_actual': 10,
            'stock_minimo': 3,
        })
        self.assertTrue(form.is_valid())

    def test_item_requiere_nombre(self):
        form = ItemInventarioForm(data={
            'categoria': self.categoria.id,
            'nombre': '',
            'unidad_medida': 'UNIDAD',
            'stock_actual': 10,
            'stock_minimo': 3,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_item_rechaza_stock_negativo(self):
        form = ItemInventarioForm(data={
            'categoria': self.categoria.id,
            'nombre': 'Rosa Azul',
            'unidad_medida': 'UNIDAD',
            'stock_actual': -5,
            'stock_minimo': 0,
        })
        self.assertFalse(form.is_valid())


class CategoriaInventarioFormTest(TestCase):
    def test_categoria_valida(self):
        form = CategoriaInventarioForm(data={'nombre': 'Cintas', 'tipo': 'INSUMO'})
        self.assertTrue(form.is_valid())

    def test_categoria_requiere_tipo(self):
        form = CategoriaInventarioForm(data={'nombre': 'Cintas', 'tipo': ''})
        self.assertFalse(form.is_valid())
# Create your tests here.
