from app import db
from datetime import datetime

class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(128), nullable=False)
    company_name = db.Column(db.String(128))
    email = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.String(256))
    message = db.Column(db.Text, nullable=False)
    meeting_date = db.Column(db.Date)
    meeting_time = db.Column(db.String(16))
    timezone = db.Column(db.String(64))
    terms_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)