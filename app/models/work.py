from app import db
from datetime import datetime

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
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
            'image_url': self.image_url,
            'bg_color': self.bg_color,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }