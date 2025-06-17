from app import db
from flask_babel import get_locale
from datetime import datetime

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_tk = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    description_ru = db.Column(db.Text)  # Хранит HTML-контент от Quill Editor
    description_tk = db.Column(db.Text)  # Хранит HTML-контент от Quill Editor
    description_en = db.Column(db.Text)  # Хранит HTML-контент от Quill Editor
    image_url = db.Column(db.String(255))
    additional_images = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    read_time = db.Column(db.String(50))
    link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'description': getattr(self, f'description_{locale}', self.description_en),
            'image_url': self.image_url,
            'additional_images': self.additional_images,
            'date': self.date.isoformat() if self.date else None,
            'read_time': self.read_time,
            'link': self.link,
            'created_at': self.created_at.isoformat()
        }