from app import db
from datetime import datetime

class PortfolioPDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pdf_file = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pdf_file": self.pdf_file
        }