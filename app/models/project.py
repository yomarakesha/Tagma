from app import db
from flask_babel import get_locale
from datetime import datetime
from app.models.category import project_category, Category

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_tk = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    description_ru = db.Column(db.Text)
    description_tk = db.Column(db.Text)
    description_en = db.Column(db.Text)
    background_image_url = db.Column(db.String(255))
    button_text_ru = db.Column(db.String(255))
    button_text_tk = db.Column(db.String(255))
    button_text_en = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    deliverables_ru = db.Column(db.Text)
    deliverables_tk = db.Column(db.Text)
    deliverables_en = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    categories = db.relationship('Category', secondary=project_category, backref=db.backref('projects', lazy='dynamic'))

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'description': getattr(self, f'description_{locale}', self.description_en),
            'background_image_url': self.background_image_url,
            'button_text': getattr(self, f'button_text_{locale}', self.button_text_en),
            'button_link': self.button_link,
            'deliverables': getattr(self, f'deliverables_{locale}', self.deliverables_en),
            'categories': [category.to_dict() for category in self.categories],
            'created_at': self.created_at.isoformat()
        }