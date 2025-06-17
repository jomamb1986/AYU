import unittest
from app import create_app, db
from app.models.user import User
from config import TestConfig
from flask import url_for

class AuthRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Crear usuarios de prueba
        self.test_user = User(username='usuario_prueba', email='prueba@example.com', role='user')
        self.test_user.set_password('clave123')
        self.admin_user = User(username='admin_prueba', email='admin@example.com', role='admin')
        self.admin_user.set_password('adminclave')
        db.session.add_all([self.test_user, self.admin_user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)

    def test_login_page_loads(self):
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Asumo que los templates siguen en inglés por ahora

    def test_successful_login_user(self):
        response = self.login('usuario_prueba', 'clave123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, usuario_prueba!', response.data)
        # Verificar redirección al dashboard de usuario o página principal de botellones
        self.assertTrue(any(msg in response.data for msg in [b'Welcome, usuario_prueba!', b'Dashboard', b'Oxygen Cylinders']))

    def test_successful_login_admin(self):
        response = self.login('admin_prueba', 'adminclave')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, admin_prueba!', response.data)
        self.assertIn(b'Admin Dashboard', response.data) # Verificar redirección al dashboard de admin

    def test_login_invalid_credentials(self):
        response = self.login('usuario_prueba', 'claveincorrecta')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_logout(self):
        self.login('usuario_prueba', 'clave123')
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)
        self.assertIn(b'Welcome to Oxygen Cylinder Management', response.data) # Redirigido a la página de bienvenida

    def test_registration_page_loads(self):
        response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_user_registration(self):
        response = self.client.post(url_for('auth.register'), data=dict(
            username='nuevo_usuario',
            email='nuevo@example.com',
            password='nuevaclave',
            password2='nuevaclave'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)
        self.assertIn(b'Sign In', response.data) # Redirigido a la página de login
        user = User.query.filter_by(username='nuevo_usuario').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'nuevo@example.com')
        self.assertEqual(user.role, 'user') # No es el primer usuario, rol 'user'

    def test_first_user_is_admin(self):
        # Limpiar usuarios existentes para esta prueba específica
        db.session.query(User).delete()
        db.session.commit()

        response = self.client.post(url_for('auth.register'), data=dict(
            username='primer_admin',
            email='primer@example.com',
            password='adminclave',
            password2='adminclave'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Congratulations, you are now the first registered admin user!', response.data)
        user = User.query.filter_by(username='primer_admin').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'admin')

        # Restaurar usuarios para otras pruebas (setUp se encarga de esto en la próxima ejecución de prueba)

    def test_registration_duplicate_username(self):
        response = self.client.post(url_for('auth.register'), data=dict(
            username='usuario_prueba', # Nombre de usuario existente
            email='nuevo2@example.com',
            password='nuevaclave',
            password2='nuevaclave'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different username.', response.data)

    def test_access_protected_route_anonymous(self):
        response = self.client.get(url_for('main.dashboard'), follow_redirects=True) # Asumiendo 'main.dashboard' es una ruta protegida
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access this page.', response.data) # Mensaje de Flask-Login
        self.assertIn(b'Sign In', response.data) # Redirigido a login

    def test_access_admin_route_as_user(self):
        self.login('usuario_prueba', 'clave123')
        response = self.client.get(url_for('admin.dashboard'), follow_redirects=True) # Ruta de admin
        # Check if the response status code is 403 (Forbidden)
        self.assertEqual(response.status_code, 403)
        # Check if the custom 403 error page content is present
        self.assertIn(b'Forbidden', response.data)
        self.logout()
