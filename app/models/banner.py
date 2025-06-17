from app import db
from flask_babel import get_locale
from datetime import datetime

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    title_ru = db.Column(db.String(255), nullable=False)
    title_tk = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    subtitle_ru = db.Column(db.String(255))
    subtitle_tk = db.Column(db.String(255))
    subtitle_en = db.Column(db.String(255))
    button_text_ru = db.Column(db.String(100))
    button_text_tk = db.Column(db.String(100))
    button_text_en = db.Column(db.String(100))

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'subtitle': getattr(self, f'subtitle_{locale}', self.subtitle_en),
            'image_url': self.image_url,
            'button_text': getattr(self, f'button_text_{locale}', self.button_text_en),
            'button_link': self.button_link,
            'created_at': self.created_at.isoformat()
        }