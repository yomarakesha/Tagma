from app import db
from flask_babel import get_locale
from datetime import datetime

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'logo_url': self.logo_url,
            'created_at': self.created_at.isoformat()
        }