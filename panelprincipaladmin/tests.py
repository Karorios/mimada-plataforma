from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalogo.models import Categoria, Producto

Usuario = get_user_model()


class PanelPrincipalAdminDashboardTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create_user(
            username='cliente@ejemplo.com', email='cliente@ejemplo.com', password='ClaveSegura123'
        )
        self.admin = Usuario.objects.create_user(
            username='admin@ejemplo.com', email='admin@ejemplo.com', password='ClaveSegura123'
        )
        self.admin.es_admin = True
        self.admin.save()

        self.categoria = Categoria.objects.create(nombre='FLORES')
        self.producto = Producto.objects.create(
            categoria=self.categoria, nombre='Ramo de rosas rojas', precio=50000,
        )

    def test_dashboard_redirige_si_no_esta_logueado(self):
        response = self.client.get(reverse('panelprincipaladmin:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_prohibido_si_no_es_admin(self):
        self.client.login(username='cliente@ejemplo.com', password='ClaveSegura123')
        response = self.client.get(reverse('panelprincipaladmin:dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_ok_si_es_admin(self):
        self.client.login(username='admin@ejemplo.com', password='ClaveSegura123')
        response = self.client.get(reverse('panelprincipaladmin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panelprincipaladmin/dashboard.html')

    def test_dashboard_muestra_productos(self):
        self.client.login(username='admin@ejemplo.com', password='ClaveSegura123')
        response = self.client.get(reverse('panelprincipaladmin:dashboard'))
        self.assertContains(response, 'Ramo de rosas rojas')