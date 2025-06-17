from app import db
from flask_babel import get_locale
from datetime import datetime

project_category = db.Table('project_category',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(255), nullable=False)
    name_tk = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        locale = str(get_locale()) or 'en'
        return getattr(self, f'name_{locale}', self.name_en)

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'name': getattr(self, f'name_{locale}', self.name_en)
        }