from app import db
from flask_babel import get_locale
from datetime import datetime

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_tk = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    subtitle_ru = db.Column(db.String(255))
    subtitle_tk = db.Column(db.String(255))
    subtitle_en = db.Column(db.String(255))
    description1_ru = db.Column(db.Text)
    description1_tk = db.Column(db.Text)
    description1_en = db.Column(db.Text)
    description2_ru = db.Column(db.Text)
    description2_tk = db.Column(db.Text)
    description2_en = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'subtitle': getattr(self, f'subtitle_{locale}', self.subtitle_en),
            'description1': getattr(self, f'description1_{locale}', self.description1_en),
            'description2': getattr(self, f'description2_{locale}', self.description2_en),
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }