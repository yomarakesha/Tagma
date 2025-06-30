from app import db
from datetime import datetime

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_url = db.Column(db.String(255))
    default_logo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'logo_url': self.logo_url,
            'default_logo': self.default_logo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }