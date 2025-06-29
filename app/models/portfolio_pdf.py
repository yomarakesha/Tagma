from app import db

class PortfolioPDF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pdf_file = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<PortfolioPDF {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "pdf_file": self.pdf_file
        }