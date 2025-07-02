from app import db
from flask_babel import get_locale

class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(128), nullable=False)
    name_en = db.Column(db.String(128), nullable=False)
    logo_url = db.Column(db.String(256), nullable=False)
    description_ru = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'name': getattr(self, f'name_{locale}', self.name_en),
            'logo_url': self.logo_url,
            'description': getattr(self, f'description_{locale}', self.description_en),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }