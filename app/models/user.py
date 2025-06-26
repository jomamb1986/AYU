# <!-- este es el codigo para app/models/user.py con tokens para reseteo de contraseña (Jules) -->
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
import jwt
from datetime import datetime, timezone, timedelta # Asegurar timedelta
from sqlalchemy import desc
from app.models.historial import HistorialMovimiento # IMPORTANTE

# Importación tentativa de HistorialMovimiento para la relación
# Esto puede necesitar ajustes si causa importación circular, en cuyo caso se usan strings.
# Para que el order_by funcione con la clase, es mejor importarla.
# Si HistorialMovimiento está en app/models/historial.py:
try:
    from app.models.historial import HistorialMovimiento
except ImportError:
    HistorialMovimiento = None # Fallback si hay problemas de importación en la definición de clase

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    nombre = db.Column(db.String(64), index=True, nullable=True)
    apellidos = db.Column(db.String(128), index=True, nullable=True)
    role = db.Column(db.String(10), default='user', nullable=False)

    movimientos_registrados = db.relationship(
        'HistorialMovimiento',
        foreign_keys='HistorialMovimiento.user_id', # Especificar explícitamente la FK
        backref=db.backref('usuario', lazy='joined'),
        lazy='dynamic',
        order_by=lambda: desc(HistorialMovimiento.fecha_movimiento) if HistorialMovimiento else 'historial_movimiento.fecha_movimiento DESC' # Lambda para ordenamiento diferido
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in_seconds=600):
        try:
            payload = {
                'reset_password_user_id': self.id,
                'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
            }
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        except Exception as e:
            current_app.logger.error(f"Error al generar token JWT: {e}")
            return None

    @staticmethod
    def verify_reset_password_token(token):
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = payload.get('reset_password_user_id')
            if user_id is None: return None
            return User.query.get(user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
            current_app.logger.info(f"Error o token inválido/expirado al verificar reseteo: {e}")
            return None

    def __repr__(self):
        return f'<User {self.username}>'
