from app import db
from datetime import datetime
from flask_babel import get_locale
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint

project_category = db.Table(
    'project_category',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    description_ru = db.Column(db.Text)
    description_en = db.Column(db.Text)
    content_ru = db.Column(db.Text)
    content_en = db.Column(db.Text)
    tags_ru = db.Column(db.PickleType)
    tags_en = db.Column(db.PickleType)
    main_image = db.Column(db.String(255))
    images = db.Column(db.PickleType)
    bg_color = db.Column(db.String(32))
    type = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    categories = db.relationship('Category', secondary=project_category, backref=db.backref('projects', lazy='dynamic'))

    # Ограничение на значения типа
    @validates('type')
    def validate_type(self, key, value):
        if value not in ['branding', 'ozers']:
            raise ValueError("Тип проекта должен быть 'branding' или 'ozers'")
        return value

    __table_args__ = (
        CheckConstraint("type IN ('branding', 'ozers')", name='check_project_type'),
    )

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'description': getattr(self, f'description_{locale}', self.description_en),
            'content': getattr(self, f'content_{locale}', self.content_en),
            "tags": (getattr(self, f"tags_{locale}", None) or []) or ["Branding", "Design"],
            'main_image': self.main_image,
            'images': self.images or [],
            'bg_color': self.bg_color,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'categories': [c.to_dict() for c in self.categories]
        }
