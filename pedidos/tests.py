from datetime import date, timedelta
from django.test import TestCase
from .forms import PedidoForm
from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class PedidoFormTest(TestCase):

    def setUp(self):
        self.fecha_valida = (date.today() + timedelta(days=3)).isoformat()
        self.datos_base = {
            'tipo_entrega': 'SOACHA',
            'es_regalo': True,          # ver nota sobre el bug más abajo
            'entrega_anonima': True,    # ver nota sobre el bug más abajo
            'nombre_destinatario': 'Juan Pérez',
            'telefono_destinatario': '3001234567',
            'mensaje': '',
            'direccion': '',
            'barrio': '',
            'ciudad': 'Bogotá',
            'referencia': '',
            'fecha_entrega': self.fecha_valida,
            'hora_entrega': '08:00 - 10:00',
        }

    def test_pedido_valido_recogida(self):
        form = PedidoForm(data=self.datos_base)
        self.assertTrue(form.is_valid())

    def test_pedido_domicilio_requiere_direccion_y_barrio(self):
        datos = self.datos_base.copy()
        datos['tipo_entrega'] = 'DOMICILIO'
        form = PedidoForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('direccion', form.errors)
        self.assertIn('barrio', form.errors)

    def test_pedido_domicilio_valido_con_direccion_y_barrio(self):
        datos = self.datos_base.copy()
        datos.update({
            'tipo_entrega': 'DOMICILIO',
            'direccion': 'Calle 10 #5-20',
            'barrio': 'Centro',
        })
        form = PedidoForm(data=datos)
        self.assertTrue(form.is_valid())

    def test_pedido_requiere_nombre_destinatario(self):
        datos = self.datos_base.copy()
        datos['nombre_destinatario'] = ''
        form = PedidoForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_pedido_requiere_telefono_destinatario(self):
        datos = self.datos_base.copy()
        datos['telefono_destinatario'] = ''
        form = PedidoForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_pedido_requiere_hora_entrega(self):
        datos = self.datos_base.copy()
        datos['hora_entrega'] = ''
        form = PedidoForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_pedido_mensaje_es_opcional(self):
        form = PedidoForm(data=self.datos_base)
        self.assertTrue(form.is_valid())

    def test_pedido_fecha_manana_no_es_valida(self):
        """Solo 1 día de anticipación no alcanza (se exigen mínimo 2)."""
        datos = self.datos_base.copy()
        datos['fecha_entrega'] = (date.today() + timedelta(days=1)).isoformat()
        form = PedidoForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_entrega', form.errors)

    def test_pedido_fecha_hoy_no_es_valida(self):
        datos = self.datos_base.copy()
        datos['fecha_entrega'] = date.today().isoformat()
        form = PedidoForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_pedido_fecha_con_dos_dias_si_es_valida(self):
        """El límite exacto: 2 días de anticipación sí debe pasar."""
        datos = self.datos_base.copy()
        datos['fecha_entrega'] = (date.today() + timedelta(days=2)).isoformat()
        form = PedidoForm(data=datos)
        self.assertTrue(form.is_valid())

    def test_pedido_es_regalo_false_es_valido(self):
        """
        Confirmado con la corrida real: omitir 'es_regalo' (equivalente a
        desmarcarlo / False, lo normal en un pedido) SÍ es válido. No hay
        bug aquí, a diferencia de lo que se predijo inicialmente.
        """
        datos = self.datos_base.copy()
        datos.pop('es_regalo')
        form = PedidoForm(data=datos)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['es_regalo'])

    Usuario = get_user_model()

    def datos_pedido_validos(**overrides):
        """Payload base válido para PedidoForm, listo para sobreescribir campos puntuales."""
        datos = {
            'tipo_entrega': 'SOACHA',
            'es_regalo': False,
            'entrega_anonima': False,
            'nombre_destinatario': 'Juan Pérez',
            'telefono_destinatario': '3001234567',
            'mensaje': '',
            'direccion': '',
            'barrio': '',
            'ciudad': 'Bogotá',
            'referencia': '',
            'fecha_entrega': (date.today() + timedelta(days=3)).isoformat(),
            'hora_entrega': '08:00 - 10:00',
        }
        datos.update(overrides)
        return datos

    class PedidosInicioTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.otro = Usuario.objects.create_user(
                username='otro@ejemplo.com', email='otro@ejemplo.com', password='ClaveSegura123'
            )
            self.pedido_propio = Pedido.objects.create(cliente=self.usuario, direccion='Calle 1', total=50000)
            self.pedido_ajeno = Pedido.objects.create(cliente=self.otro, direccion='Calle 2', total=30000)

        def test_inicio_redirige_si_no_esta_logueado(self):
            response = self.client.get(reverse('pedidos:inicio'))
            self.assertEqual(response.status_code, 302)

        def test_inicio_muestra_solo_pedidos_propios(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:inicio'))
            self.assertEqual(response.status_code, 200)
            pedidos_mostrados = list(response.context['pedidos'])
            self.assertIn(self.pedido_propio, pedidos_mostrados)
            self.assertNotIn(self.pedido_ajeno, pedidos_mostrados)

    class CarritoTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.categoria = Categoria.objects.create(nombre='FLORES')
            self.producto = Producto.objects.create(
                categoria=self.categoria, nombre='Ramo de rosas rojas', precio=50000,
            )

        def test_agregar_al_carrito_requiere_login(self):
            response = self.client.post(
                reverse('pedidos:agregar_al_carrito', args=[self.producto.pk]), data={'cantidad': 2}
            )
            self.assertEqual(response.status_code, 302)

        def test_agregar_al_carrito_agrega_item(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.post(
                reverse('pedidos:agregar_al_carrito', args=[self.producto.pk]), data={'cantidad': 2}
            )
            self.assertEqual(response.status_code, 302)
            carrito = self.client.session.get('carrito', [])
            self.assertEqual(len(carrito), 1)
            self.assertEqual(carrito[0]['producto_id'], self.producto.id)
            self.assertEqual(carrito[0]['cantidad'], 2)

        def test_ver_carrito_muestra_items_y_total(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self.client.post(reverse('pedidos:agregar_al_carrito', args=[self.producto.pk]), data={'cantidad': 3})
            response = self.client.get(reverse('pedidos:ver_carrito'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Ramo de rosas rojas')
            self.assertEqual(response.context['total_carrito'], Decimal('150000'))

        def test_eliminar_del_carrito_quita_item(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self.client.post(reverse('pedidos:agregar_al_carrito', args=[self.producto.pk]), data={'cantidad': 1})
            item_id = self.client.session['carrito'][0]['id']
            response = self.client.get(reverse('pedidos:eliminar_del_carrito', args=[item_id]))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(self.client.session.get('carrito', []), [])

        def test_actualizar_cantidad_carrito(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self.client.post(reverse('pedidos:agregar_al_carrito', args=[self.producto.pk]), data={'cantidad': 1})
            item_id = self.client.session['carrito'][0]['id']
            response = self.client.post(
                reverse('pedidos:actualizar_cantidad_carrito', args=[item_id]), data={'cantidad': 5}
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(self.client.session['carrito'][0]['cantidad'], 5)

    class CrearPedidoProductoTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.categoria = Categoria.objects.create(nombre='FLORES')
            self.producto = Producto.objects.create(
                categoria=self.categoria, nombre='Ramo de rosas rojas', precio=50000,
            )

        def test_crear_pedido_requiere_login(self):
            response = self.client.get(reverse('pedidos:crear_pedido', args=[self.producto.pk]))
            self.assertEqual(response.status_code, 302)

        def test_crear_pedido_get_muestra_formulario(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:crear_pedido', args=[self.producto.pk]) + '?cantidad=2')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['cantidad'], 2)

        def test_crear_pedido_post_valido_guarda_en_sesion_y_redirige(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.post(
                reverse('pedidos:crear_pedido', args=[self.producto.pk]) + '?cantidad=2',
                data=datos_pedido_validos(),
            )
            self.assertRedirects(response, reverse('pedidos:resumen'))
            items = self.client.session['items_pedido']
            self.assertEqual(items[0]['producto_id'], self.producto.id)
            self.assertEqual(items[0]['cantidad'], 2)

    class ResumenTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.categoria = Categoria.objects.create(nombre='FLORES')
            self.producto = Producto.objects.create(
                categoria=self.categoria, nombre='Ramo de rosas rojas', precio=50000,
            )

        def _sesion_con_pedido(self, tipo_entrega='DOMICILIO'):
            session = self.client.session
            session['pedido'] = datos_pedido_validos(
                tipo_entrega=tipo_entrega, direccion='Calle 1', barrio='Centro'
            )
            session['items_pedido'] = [{'tipo': 'producto', 'producto_id': self.producto.id, 'cantidad': 2}]
            session.save()

        def test_resumen_redirige_si_no_hay_pedido_en_sesion(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:resumen'))
            self.assertRedirects(response, reverse('pedidos:inicio'))

        def test_resumen_muestra_total_con_domicilio(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self._sesion_con_pedido('DOMICILIO')
            response = self.client.get(reverse('pedidos:resumen'))
            self.assertEqual(response.status_code, 200)
            # 2 x 50000 + 8000 de domicilio
            self.assertEqual(response.context['total'], Decimal('108000'))

        def test_resumen_sin_domicilio_en_recogida(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self._sesion_con_pedido('SOACHA')
            response = self.client.get(reverse('pedidos:resumen'))
            self.assertEqual(response.context['valor_domicilio'], 0)
            self.assertEqual(response.context['total'], Decimal('100000'))

    class ConfirmarPedidoTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.categoria = Categoria.objects.create(nombre='FLORES')
            self.producto = Producto.objects.create(
                categoria=self.categoria, nombre='Ramo de rosas rojas', precio=50000,
            )

        def _sesion_con_pedido(self):
            session = self.client.session
            session['pedido'] = datos_pedido_validos()
            session['items_pedido'] = [{'tipo': 'producto', 'producto_id': self.producto.id, 'cantidad': 2}]
            session.save()

        def test_confirmar_redirige_si_no_hay_pedido_en_sesion(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:confirmar_pedido'))
            self.assertRedirects(response, reverse('pedidos:inicio'))

        def test_confirmar_crea_pedido_y_detalle_y_limpia_sesion(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self._sesion_con_pedido()
            response = self.client.get(reverse('pedidos:confirmar_pedido'))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('https://wa.me/'))

            pedido = Pedido.objects.get(cliente=self.usuario)
            self.assertEqual(pedido.total, Decimal('100000'))
            self.assertEqual(DetallePedido.objects.filter(pedido=pedido).count(), 1)

            self.assertNotIn('pedido', self.client.session)
            self.assertNotIn('items_pedido', self.client.session)

    class EditarPedidoTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.otro = Usuario.objects.create_user(
                username='otro@ejemplo.com', email='otro@ejemplo.com', password='ClaveSegura123'
            )
            self.pedido = Pedido.objects.create(
                cliente=self.usuario, direccion='Calle 1', barrio='Centro', ciudad='Bogotá',
                tipo_entrega='DOMICILIO', total=50000, estado='PENDIENTE',
            )

        def test_editar_pedido_de_otro_usuario_da_404(self):
            self.client.login(username='otro@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:editar_pedido', args=[self.pedido.id]))
            self.assertEqual(response.status_code, 404)

        def test_editar_pedido_no_pendiente_redirige(self):
            self.pedido.estado = 'CONFIRMADO'
            self.pedido.save()
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:editar_pedido', args=[self.pedido.id]))
            self.assertRedirects(response, reverse('pedidos:inicio'))

        def test_editar_pedido_post_valido_actualiza(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            datos = datos_pedido_validos(
                tipo_entrega='DOMICILIO', direccion='Calle nueva 2', barrio='Centro',
                telefono_destinatario='3009999999',
            )
            response = self.client.post(reverse('pedidos:editar_pedido', args=[self.pedido.id]), data=datos)
            self.assertRedirects(response, reverse('pedidos:inicio'))
            self.pedido.refresh_from_db()
            self.assertEqual(self.pedido.direccion, 'Calle nueva 2')

    class CancelarPedidoTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.pedido = Pedido.objects.create(
                cliente=self.usuario, direccion='Calle 1', total=50000, estado='PENDIENTE',
            )

        def test_cancelar_pedido_pendiente_cambia_estado(self):
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            response = self.client.get(reverse('pedidos:cancelar_pedido', args=[self.pedido.id]))
            self.assertEqual(response.status_code, 302)
            self.pedido.refresh_from_db()
            self.assertEqual(self.pedido.estado, 'CANCELADO')

        def test_cancelar_pedido_no_pendiente_no_cambia(self):
            self.pedido.estado = 'ENTREGADO'
            self.pedido.save()
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self.client.get(reverse('pedidos:cancelar_pedido', args=[self.pedido.id]))
            self.pedido.refresh_from_db()
            self.assertEqual(self.pedido.estado, 'ENTREGADO')

    class IniciarPedidoSeleccionadosTest(TestCase):

        def setUp(self):
            self.usuario = Usuario.objects.create_user(
                username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
            )
            self.categoria = Categoria.objects.create(nombre='FLORES')
            self.producto = Producto.objects.create(
                categoria=self.categoria, nombre='Ramo de rosas rojas', precio=50000,
            )
            self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
            self.client.post(reverse('pedidos:agregar_al_carrito', args=[self.producto.pk]), data={'cantidad': 1})

        def test_iniciar_pedido_sin_seleccion_da_error(self):
            response = self.client.post(reverse('pedidos:iniciar_pedido_seleccionados'), data={})
            self.assertRedirects(response, reverse('pedidos:ver_carrito'))
            self.assertNotIn('items_pedido', self.client.session)

        def test_iniciar_pedido_con_seleccion_arma_items_pedido(self):
            item_id = self.client.session['carrito'][0]['id']
            response = self.client.post(
                reverse('pedidos:iniciar_pedido_seleccionados'), data={'item_ids': [item_id]}
            )
            self.assertRedirects(response, reverse('pedidos:crear_pedido_lote'))
            items = self.client.session['items_pedido']
            self.assertEqual(items[0]['producto_id'], self.producto.id)
            self.assertEqual(items[0]['cart_item_id'], item_id)
            # el carrito NO se debe vaciar todavía en este paso
            self.assertEqual(len(self.client.session['carrito']), 1)



