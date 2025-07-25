﻿from app import db
from datetime import datetime
from flask_babel import get_locale

service_blog = db.Table(
    'service_blog',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')),
    db.Column('blog_id', db.Integer, db.ForeignKey('blog.id'))
)

service_project = db.Table(
    'service_project',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_ru = db.Column(db.Text)
    content_en = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='services')
    projects = db.relationship('Project', secondary=service_project, backref='services')
    blogs = db.relationship('Blog', secondary=service_blog, backref='services')

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'content': getattr(self, f'content_{locale}', self.content_en),
            'category': self.category.to_dict() if self.category else None,
            'projects': [p.to_dict() for p in self.projects],
            'blogs': [b.to_dict() for b in self.blogs],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
