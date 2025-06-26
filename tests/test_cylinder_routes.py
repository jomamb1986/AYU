import unittest
from app import create_app, db
from app.models.user import User
from app.models.cylinder import Cylinder
from config import TestConfig
from flask import url_for
from datetime import datetime # Para verificar fechas

class CylinderRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Crear usuarios y botellones de prueba
        self.user = User(username='usuario_botellon', email='botellon@example.com', role='user')
        self.user.set_password('clavebotellon')
        self.admin = User(username='admin_botellon', email='admin_botellon@example.com', role='admin')
        self.admin.set_password('adminclavebotellon')
        db.session.add_all([self.user, self.admin])
        db.session.commit()

        self.c1 = Cylinder(cylinder_id_tag='BOT001', status='available') # Corrected status to match default/logic
        self.c2 = Cylinder(cylinder_id_tag='BOT002', status='delivered', delivery_date=datetime.utcnow())
        db.session.add_all([self.c1, self.c2])
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

    def test_view_cylinders_list_authenticated_user(self):
        self.login('usuario_botellon', 'clavebotellon')
        response = self.client.get(url_for('cylinders.index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Oxygen Cylinders', response.data)
        self.assertIn(b'BOT001', response.data)
        self.assertIn(b'BOT002', response.data)
        self.logout()

    def test_view_cylinders_list_anonymous(self):
        response = self.client.get(url_for('cylinders.index'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access this page.', response.data)

    def test_create_cylinder_page_loads_authenticated(self):
        self.login('usuario_botellon', 'clavebotellon')
        response = self.client.get(url_for('cylinders.create_cylinder'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Cylinder', response.data)
        self.logout()

    def test_create_new_cylinder_success(self):
        self.login('usuario_botellon', 'clavebotellon')
        initial_cylinder_count = Cylinder.query.count()
        response = self.client.post(url_for('cylinders.create_cylinder'), data=dict(
            cylinder_id_tag='NUEVOBOT003'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cylinder NUEVOBOT003 has been created successfully!', response.data)
        self.assertIn(b'NUEVOBOT003', response.data)
        self.assertEqual(Cylinder.query.count(), initial_cylinder_count + 1)
        cylinder = Cylinder.query.filter_by(cylinder_id_tag='NUEVOBOT003').first()
        self.assertIsNotNone(cylinder)
        self.assertEqual(cylinder.status, 'available')
        self.logout()

    def test_create_cylinder_duplicate_id(self):
        self.login('usuario_botellon', 'clavebotellon')
        response = self.client.post(url_for('cylinders.create_cylinder'), data=dict(
            cylinder_id_tag='BOT001'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This Cylinder ID Tag is already registered.', response.data)
        self.logout()

    def test_view_single_cylinder_authenticated(self):
        self.login('usuario_botellon', 'clavebotellon')
        response = self.client.get(url_for('cylinders.view_cylinder', cylinder_id=self.c1.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cylinder Details: BOT001', response.data)
        self.assertIn(b'Status:', response.data)
        self.assertIn(b'Available', response.data)
        self.logout()

    def test_update_cylinder_status_page_loads(self):
        self.login('usuario_botellon', 'clavebotellon')
        response = self.client.get(url_for('cylinders.update_cylinder_status', cylinder_id=self.c1.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Update Status for Cylinder: BOT001', response.data)
        self.logout()

    def test_update_cylinder_status_to_delivered_success(self):
        self.login('usuario_botellon', 'clavebotellon')
        response = self.client.post(url_for('cylinders.update_cylinder_status', cylinder_id=self.c1.id), data=dict(
            status='delivered'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Status for cylinder BOT001 has been updated to delivered.', response.data)
        self.assertIn(b'Delivered', response.data)
        updated_cylinder = Cylinder.query.get(self.c1.id)
        self.assertEqual(updated_cylinder.status, 'delivered')
        self.assertIsNotNone(updated_cylinder.delivery_date)
        self.assertIsNone(updated_cylinder.reception_date)
        self.logout()

    def test_update_cylinder_status_to_received_success(self):
        self.login('usuario_botellon', 'clavebotellon')

        self.client.post(url_for('cylinders.update_cylinder_status', cylinder_id=self.c1.id), data=dict(status='delivered'), follow_redirects=True)

        response = self.client.post(url_for('cylinders.update_cylinder_status', cylinder_id=self.c1.id), data=dict(
            status='received'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Status for cylinder BOT001 has been updated to received.', response.data)
        self.assertIn(b'Received', response.data)
        updated_cylinder = Cylinder.query.get(self.c1.id)
        self.assertEqual(updated_cylinder.status, 'received')
        self.assertIsNotNone(updated_cylinder.reception_date)
        self.logout()

    def test_delete_cylinder_by_admin(self):
        self.login('admin_botellon', 'adminclavebotellon')
        cylinder_to_delete_id = self.c2.id
        cylinder_to_delete_tag = self.c2.cylinder_id_tag
        initial_cylinder_count = Cylinder.query.count()

        response = self.client.post(url_for('cylinders.delete_cylinder', cylinder_id=cylinder_to_delete_id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Cylinder {cylinder_to_delete_tag} has been deleted.'.encode(), response.data)
        self.assertIsNone(Cylinder.query.get(cylinder_to_delete_id))
        self.assertEqual(Cylinder.query.count(), initial_cylinder_count - 1)
        self.logout()

    def test_delete_cylinder_by_non_admin(self):
        self.login('usuario_botellon', 'clavebotellon')
        initial_cylinder_count = Cylinder.query.count()
        response = self.client.post(url_for('cylinders.delete_cylinder', cylinder_id=self.c1.id), follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Forbidden', response.data)
        self.assertIsNotNone(Cylinder.query.get(self.c1.id))
        self.assertEqual(Cylinder.query.count(), initial_cylinder_count)
        self.logout()
