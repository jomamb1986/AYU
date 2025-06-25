# <!-- este es el codigo para app/models/cylinder.py con borrado lógico -->
from app import db
from datetime import datetime
from app.models.historial import HistorialMovimiento # Asegurarse de que esta importación esté

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

    ##esta_activo = db.Column(db.Boolean, default=True, nullable=False, index=True)##habilitar esto para produccion
    
    esta_activo = db.Column(db.Boolean, default=True, nullable=True, index=True)##solo para pruebas

    historial_movimientos = db.relationship(
        'HistorialMovimiento', 
        backref='cilindro',
        lazy='dynamic', 
        # cascade="all, delete-orphan", # <--- LÍNEA ELIMINADA/COMENTADA
        order_by='HistorialMovimiento.fecha_movimiento.desc()'
    )

    def __repr__(self):
        return '<Cylinder {}>'.format(self.cylinder_id_tag)
