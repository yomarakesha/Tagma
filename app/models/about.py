from app import db

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    # Связь с AboutItem
    items = db.relationship('AboutItem', backref='about', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'items': [item.to_dict() for item in self.items]
        }

class AboutItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about_id = db.Column(db.Integer, db.ForeignKey('about.id'))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    background_image_url = db.Column(db.String(255))
    button_text = db.Column(db.String(255))
    button_link = db.Column(db.String(255))
    deliverables = db.Column(db.Text)
    color = db.Column(db.String(32))
    type = db.Column(db.String(64))
    created_at = db.Column(db.DateTime)
    # Категории для AboutItem (многие ко многим)
    categories = db.relationship('Category', secondary='aboutitem_category', backref='about_items')

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

aboutitem_category = db.Table(
    'aboutitem_category',
    db.Column('aboutitem_id', db.Integer, db.ForeignKey('about_item.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)