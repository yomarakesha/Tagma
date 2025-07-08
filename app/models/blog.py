from app import db
from datetime import datetime
from sqlalchemy.types import PickleType
from flask_babel import get_locale

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    description_ru = db.Column(db.Text)
    description_en = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    additional_images = db.Column(db.Text)
    date = db.Column(db.Date)
    read_time = db.Column(db.String(50))
    link = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True)
    tags = db.Column(PickleType)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'slug': self.slug,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_time': int(self.read_time) if self.read_time and self.read_time.isdigit() else self.read_time,
            'tags': self.tags or [],
            'description': getattr(self, f'description_{locale}', self.description_en)
        }
