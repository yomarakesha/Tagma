from app import db
from datetime import datetime

project_category = db.Table(
    'project_category',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    background_image_url = db.Column(db.String(255))
    button_text = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    deliverables = db.Column(db.Text)
    color = db.Column(db.String(32))
    type = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    categories = db.relationship('Category', secondary=project_category, backref=db.backref('projects', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'background_image_url': self.background_image_url,
            'button_text': self.button_text,
            'button_link': self.button_link,
            'deliverables': self.deliverables,
            'color': self.color,
            'type': self.type,
            'categories': [c.to_dict() for c in self.categories],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }