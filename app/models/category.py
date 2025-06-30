from app import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255))
    link = db.Column(db.String(255))
    bg_color = db.Column(db.String(32))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'link': self.link,
            'bg_color': self.bg_color,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }