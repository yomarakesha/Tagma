from app import db

class ContactRequest(db.Model):
    id = db.Column(db.String(32), primary_key=True)  # строковый id
    full_name = db.Column(db.String(128), nullable=False)
    company_name = db.Column(db.String(128))
    email = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(64), nullable=False)
    subject = db.Column(db.String(256))
    message = db.Column(db.Text, nullable=False)
    meeting_date = db.Column(db.String(64))  # строка, а не Date
    meeting_time = db.Column(db.String(16))
    timezone = db.Column(db.String(64))
    terms_accepted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'meeting_date': self.meeting_date,
            'meeting_time': self.meeting_time,
            'message': self.message,
            'phone': self.phone,
            'subject': self.subject,
            'terms_accepted': self.terms_accepted,
            'timezone': self.timezone,
            'company_name': self.company_name
        }