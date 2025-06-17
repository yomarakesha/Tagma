from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

def init_api(app):
    from app.api.resources import BannerResource, ProjectResource, BlogResource
    api.add_resource(BannerResource, '/banners', '/banners/<int:banner_id>')
    api.add_resource(ProjectResource, '/projects', '/projects/<int:project_id>')
    api.add_resource(BlogResource, '/blog', '/blog/<int:blog_id>')
    app.register_blueprint(api_bp, url_prefix='/api')