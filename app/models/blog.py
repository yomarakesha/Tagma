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
    additional_images = db.Column(db.PickleType)
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
            'description': getattr(self, f'description_{locale}', self.description_en),
            'image_url': self.image_url,
            'additional_images': self.additional_images if isinstance(self.additional_images, list) else [],
            'date': self.date.isoformat() if self.date else None,
            'read_time': self.read_time or "3 min read",
            'link': self.link or self.slug or "",
            'slug': self.slug or "",
            'tags': self.tags if isinstance(self.tags, list) else [],
            'categories': [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

from sqlalchemy import event
from app.utils.slugify import slugify

@event.listens_for(Blog, 'before_insert')
@event.listens_for(Blog, 'before_update')
def generate_blog_slug(mapper, connection, target):
    if not target.slug:
        title = target.title_en or target.title_ru
        if title:
            target.slug = slugify(title)
