from app import db
from datetime import datetime

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    additional_images = db.Column(db.Text)
    date = db.Column(db.Date)
    read_time = db.Column(db.String(50))
    link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'additional_images': self.additional_images,
            'date': self.date.isoformat() if self.date else None,
            'read_time': self.read_time,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }