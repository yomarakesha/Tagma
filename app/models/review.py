from app import db
from flask_babel import get_locale
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_ru = db.Column(db.Text)
    content_tk = db.Column(db.Text)
    content_en = db.Column(db.Text)
    author_ru = db.Column(db.String(255))
    author_tk = db.Column(db.String(255))
    author_en = db.Column(db.String(255))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref='reviews')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'content': getattr(self, f'content_{locale}', self.content_en),
            'author': getattr(self, f'author_{locale}', self.author_en),
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat()
        }