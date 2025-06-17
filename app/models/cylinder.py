from app import db
from datetime import datetime

class Cylinder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cylinder_id_tag = db.Column(db.String(64), index=True, unique=True, nullable=False) # A unique tag/ID for the cylinder itself
    status = db.Column(db.String(64), default='created') # e.g., 'created', 'received', 'delivered', 'maintenance'
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reception_date = db.Column(db.DateTime, nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    # Add more fields as necessary, e.g., location, assigned_to_user_id, notes

    def __repr__(self):
        return '<Cylinder {}>'.format(self.cylinder_id_tag)
