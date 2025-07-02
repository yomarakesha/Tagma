from app import db
from datetime import datetime
from flask_babel import get_locale

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255))
    link = db.Column(db.String(255))
    bg_color = db.Column(db.String(32))
    description_ru = db.Column(db.Text)
    description_en = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'slug': self.slug,
            'link': self.link,
            'bg_color': self.bg_color,
            'description': getattr(self, f'description_{locale}', self.description_en),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }