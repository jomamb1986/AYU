from app import db
from datetime import datetime

class HistorialMovimiento(db.Model):
    __tablename__ = 'historial_movimiento'
    id = db.Column(db.Integer, primary_key=True)
    cylinder_id = db.Column(db.Integer, db.ForeignKey('cylinder.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    tipo_movimiento = db.Column(db.String(20), nullable=False, index=True)
    fecha_movimiento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    nombre_contraparte = db.Column(db.String(150), nullable=True)
    nota = db.Column(db.Text, nullable=True)

    cilindro = db.relationship('Cylinder', backref=db.backref('historial_movimientos', lazy='dynamic', order_by=fecha_movimiento.desc()))
    usuario = db.relationship('User', backref=db.backref('movimientos_registrados', lazy='dynamic'))

    def __repr__(self):
        return f'<HistorialMovimiento ID:{self.id} CilindroID:{self.cylinder_id} UsuarioID:{self.user_id} Tipo:{self.tipo_movimiento} Fecha:{self.fecha_movimiento}>'
