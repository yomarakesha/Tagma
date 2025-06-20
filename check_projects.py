from app import create_app, db
from app.models.project import Project

app = create_app()
with app.app_context():
    projects = Project.query.all()
    for p in projects:
        print(f"ID: {p.id}, Title: {p.title_en}")