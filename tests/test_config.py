import unittest
from flask import Flask
from config import Config, TestConfig
import os

# Determinar el directorio raíz del proyecto correctamente relativo a este archivo
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestConfigTestCase(unittest.TestCase):
    def test_default_config(self):
        app = Flask(__name__)
        app.config.from_object(Config)
        self.assertFalse(app.config.get('TESTING', False)) # Por defecto TESTING es False
        expected_db_path = 'sqlite:///' + os.path.join(basedir, 'app.db')
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], expected_db_path)
        self.assertTrue(app.config.get('WTF_CSRF_ENABLED', True)) # Por defecto CSRF está habilitado

    def test_testing_config(self):
        app = Flask(__name__)
        app.config.from_object(TestConfig)
        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///:memory:')
        self.assertFalse(app.config['WTF_CSRF_ENABLED']) # CSRF deshabilitado para pruebas
