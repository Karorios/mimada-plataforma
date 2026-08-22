from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .models import Usuario


class LoginFrontTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opciones = Options()
        opciones.add_argument('--headless=new')
        opciones.add_argument('--no-sandbox')
        opciones.add_argument('--disable-dev-shm-usage')
        opciones.add_argument('--disable-gpu')
        opciones.add_argument('--window-size=1280,1024')
        cls.selenium = webdriver.Chrome(options=opciones)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='test@ejemplo.com', email='test@ejemplo.com', password='ClaveSegura123'
        )

    def test_login_exitoso_redirige(self):
        self.selenium.get(f'{self.live_server_url}/usuarios/login/')
        self.selenium.find_element(By.NAME, 'username').send_keys('test@ejemplo.com')
        self.selenium.find_element(By.NAME, 'password').send_keys('ClaveSegura123')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        self.assertNotIn('/login/', self.selenium.current_url)