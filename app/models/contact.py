from app import db
from flask_babel import get_locale
from datetime import datetime

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(255))
    address_ru = db.Column(db.String(255))
    address_tk = db.Column(db.String(255))
    address_en = db.Column(db.String(255))
    email = db.Column(db.String(255))
    social_media = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'phone': self.phone,
            'address': getattr(self, f'address_{locale}', self.address_en),
            'email': self.email,
            'social_media': self.social_media,
            'created_at': self.created_at.isoformat()
        }