﻿from app import db
from flask_babel import get_locale
from datetime import datetime

service_blog = db.Table(
    'service_blog',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True),
    db.Column('blog_id', db.Integer, db.ForeignKey('blog.id'), primary_key=True)
)

service_project = db.Table(
    'service_project',
    db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_tk = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=False)
    subtitles_ru = db.Column(db.Text)
    subtitles_tk = db.Column(db.Text)
    subtitles_en = db.Column(db.Text)
    button_text_ru = db.Column(db.String(100))
    button_text_tk = db.Column(db.String(100))
    button_text_en = db.Column(db.String(100))
    button_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    blogs = db.relationship('Blog', secondary=service_blog, backref='services')
    projects = db.relationship('Project', secondary=service_project, backref='services')

    def to_dict(self):
        locale = str(get_locale()) or 'en'
        return {
            'id': self.id,
            'title': getattr(self, f'title_{locale}', self.title_en),
            'subtitles': getattr(self, f'subtitles_{locale}', self.subtitles_en),
            'button_text': getattr(self, f'button_text_{locale}', self.button_text_en),
            'button_link': self.button_link,
            'created_at': self.created_at.isoformat(),
            'blogs': [blog.to_dict() for blog in self.blogs],
            'projects': [project.to_dict() for project in self.projects]
        }