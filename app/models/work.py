from app import db
from datetime import datetime
from sqlalchemy.types import PickleType

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)  # новое поле
    tags = db.Column(PickleType)      # новое поле (список)
    main_image = db.Column(db.String(255))  # новое поле
    content = db.Column(db.Text)
    images = db.Column(PickleType)    # новое поле (список)
    button_text = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    bg_color = db.Column(db.String(64))
    type = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'button_text': self.button_text,
            'button_link': self.button_link,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S') if self.created_at else None,
            'image_url': self.image_url,
            'bg_color': self.bg_color,
            'type': self.type
        }