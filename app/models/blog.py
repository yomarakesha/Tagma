from app import db
from datetime import datetime
from sqlalchemy.types import PickleType

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    additional_images = db.Column(db.Text)
    date = db.Column(db.Date)
    read_time = db.Column(db.String(50))
    link = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True)
    tags = db.Column(PickleType)  # или JSON, если используете PostgreSQL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_time': int(self.read_time) if self.read_time and self.read_time.isdigit() else self.read_time,
            'tags': self.tags or [],
            'description': self.description
        }