import unittest
from app import create_app, db
from app.models.user import User
from config import TestConfig

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(username='susan')
        u.set_password('gato') # 'cat' en español
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(username='susan')
        u.set_password('gato')
        with self.assertRaises(AttributeError):
            _ = u.password

    def test_password_verification(self):
        u = User(username='susan')
        u.set_password('gato')
        self.assertTrue(u.check_password('gato'))
        self.assertFalse(u.check_password('perro')) # 'dog' en español

    def test_password_salts_are_random(self):
        u1 = User(username='juan') # 'john' en español
        u1.set_password('raton') # 'mouse' en español
        u2 = User(username='juana') # 'jane' en español
        u2.set_password('raton')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_user_roles(self):
        u_user = User(username='usuario_regular', email='user@example.com', role='user')
        u_admin = User(username='usuario_admin', email='admin@example.com', role='admin')
        db.session.add_all([u_user, u_admin])
        db.session.commit()
        self.assertEqual(u_user.role, 'user')
        self.assertEqual(u_admin.role, 'admin')

        # Probar rol por defecto
        u_default = User(username='usuario_defecto', email='def@example.com')
        db.session.add(u_default)
        db.session.commit()
        self.assertEqual(u_default.role, 'user')
