import unittest
from app import create_app, db
from app.models.cylinder import Cylinder
from config import TestConfig
from datetime import datetime, timedelta

class CylinderModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_cylinder(self):
        c = Cylinder(cylinder_id_tag='B001', status='disponible') # 'available' en español
        db.session.add(c)
        db.session.commit()

        cylinder_from_db = Cylinder.query.filter_by(cylinder_id_tag='B001').first()
        self.assertIsNotNone(cylinder_from_db)
        self.assertEqual(cylinder_from_db.status, 'disponible')
        self.assertIsNotNone(cylinder_from_db.creation_date)
        self.assertIsNone(cylinder_from_db.delivery_date)
        self.assertIsNone(cylinder_from_db.reception_date)

    def test_cylinder_repr(self):
        c = Cylinder(cylinder_id_tag='B002')
        self.assertEqual(repr(c), '<Cylinder B002>')

    def test_cylinder_date_fields_basic_storage(self):
        # Prueba básica de que las fechas se pueden almacenar y recuperar.
        # La lógica de cuándo se establecen estas fechas está principalmente en las rutas.
        now = datetime.utcnow()
        creation_dt = now - timedelta(days=2)
        delivery_dt = now - timedelta(days=1)
        reception_dt = now

        c = Cylinder(
            cylinder_id_tag='B003',
            status='recibido', # 'received' en español
            creation_date=creation_dt,
            delivery_date=delivery_dt,
            reception_date=reception_dt
        )
        db.session.add(c)
        db.session.commit()

        retrieved_c = Cylinder.query.filter_by(cylinder_id_tag='B003').first()
        self.assertIsNotNone(retrieved_c)
        self.assertEqual(retrieved_c.status, 'recibido')
        self.assertEqual(retrieved_c.creation_date, creation_dt)
        self.assertEqual(retrieved_c.delivery_date, delivery_dt)
        self.assertEqual(retrieved_c.reception_date, reception_dt)
