from app import db, create_app
from app.models.project import Project
from app.models.blog import Blog
from app.models.banner import Banner
from app.models.client import Client
from app.models.about import About

app = create_app()
with app.app_context():
    # Для Project
    for project in Project.query.all():
        if project.background_image_url and 'images' in project.background_image_url:
            project.background_image_url = project.background_image_url.replace('images', 'uploads')
    
    # Для Blog
    for blog in Blog.query.all():
        if blog.image_url and 'images' in blog.image_url:
            blog.image_url = blog.image_url.replace('images', 'uploads')
    
    # Для Banner
    for banner in Banner.query.all():
        if banner.image_url and 'images' in banner.image_url:
            banner.image_url = banner.image_url.replace('images', 'uploads')
    
    # Для Client
    for client in Client.query.all():
        if client.logo_url and 'images' in client.logo_url:
            client.logo_url = client.logo_url.replace('images', 'uploads')
    
    # Для About
    for about in About.query.all():
        if about.image_url and 'images' in about.image_url:
            about.image_url = about.image_url.replace('images', 'uploads')
    
    db.session.commit()
    print("Image paths updated successfully.")