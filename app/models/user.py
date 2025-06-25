# <!-- este es el codigo CORREGIDO para app/models/user.py -->
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models.historial import HistorialMovimiento # IMPORTANTE
from sqlalchemy import desc # IMPORTANTE

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
        foreign_keys=[HistorialMovimiento.user_id],
        backref=db.backref('usuario', lazy='joined'),
        lazy='dynamic',
        order_by=desc(HistorialMovimiento.fecha_movimiento)
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.username}>'
