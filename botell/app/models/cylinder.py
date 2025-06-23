# <!-- este es el codigo para app/models/cylinder.py con marca, color, numero_serie --> #}
from app import db
from datetime import datetime

class Cylinder(db.Model):
    __tablename__ = 'cylinder'

    id = db.Column(db.Integer, primary_key=True)
    cylinder_id_tag = db.Column(db.String(64), index=True, unique=True, nullable=False)
    status = db.Column(db.String(64), default='available', nullable=False)
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reception_date = db.Column(db.DateTime, nullable=True, index=True)
    delivery_date = db.Column(db.DateTime, nullable=True, index=True)

    marca = db.Column(db.String(80), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    numero_serie = db.Column(db.String(80), nullable=True, index=True)

    def __repr__(self):
        return '<Cylinder {}>'.format(self.cylinder_id_tag)
