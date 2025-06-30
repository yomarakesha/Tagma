from app import db
from datetime import datetime

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    button_text = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'image_url': self.image_url,
            'logo_url': self.logo_url,
            'button_text': self.button_text,
            'button_link': self.button_link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }