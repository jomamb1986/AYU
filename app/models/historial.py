# <!-- este es el codigo CORREGIDO para app/models/historial.py -->
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

    # NO definimos db.relationship para 'cilindro' o 'usuario' aquí,
    # porque los backrefs desde Cylinder y User los crearán.

    def __repr__(self):
        fecha_str = self.fecha_movimiento.strftime('%Y-%m-%d %H:%M') if self.fecha_movimiento else "N/A"
        return f'<HistorialMovimiento ID:{self.id} CilindroID:{self.cylinder_id} UsuarioID:{self.user_id} Tipo:{self.tipo_movimiento} Fecha:{fecha_str}>'
