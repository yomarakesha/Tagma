from app import db
from datetime import datetime
from sqlalchemy.types import PickleType

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    description_ru = db.Column(db.Text)
    description_en = db.Column(db.Text)
    tags_ru = db.Column(PickleType)      # список тегов на русском
    tags_en = db.Column(PickleType)      # список тегов на английском
    main_image = db.Column(db.String(255))
    content_ru = db.Column(db.Text)
    content_en = db.Column(db.Text)
    images = db.Column(PickleType)
    button_text_ru = db.Column(db.String(255))
    button_text_en = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    bg_color = db.Column(db.String(64))
    type = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        from flask_babel import get_locale
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'description': getattr(self, f'description_{locale}', self.description_en),
            'content': getattr(self, f'content_{locale}', self.content_en),
            'button_text': getattr(self, f'button_text_{locale}', self.button_text_en),
            'button_link': self.button_link,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S') if self.created_at else None,
            'image_url': self.image_url,
            'bg_color': self.bg_color,
            'type': self.type,
            'tags': getattr(self, f'tags_{locale}', self.tags_en) or [],
            'images': self.images or []
        }