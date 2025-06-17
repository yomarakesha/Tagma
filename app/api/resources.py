from flask_restful import Resource, reqparse
from flask import request
from app import db
from app.models.banner import Banner
from app.models.project import Project
from app.models.blog import Blog
from app.models.category import Category, project_category

# Парсер для валидации данных Banner
banner_parser = reqparse.RequestParser()
banner_parser.add_argument('title_ru', type=str, required=True, help='Title (Russian) is required')
banner_parser.add_argument('title_tk', type=str, required=True, help='Title (Turkmen) is required')
banner_parser.add_argument('title_en', type=str, required=True, help='Title (English) is required')
banner_parser.add_argument('subtitle_ru', type=str, required=True, help='Subtitle (Russian) is required')
banner_parser.add_argument('subtitle_tk', type=str, required=True, help='Subtitle (Turkmen) is required')
banner_parser.add_argument('subtitle_en', type=str, required=True, help='Subtitle (English) is required')
banner_parser.add_argument('image_url', type=str, required=True, help='Image URL is required')
banner_parser.add_argument('button_text_ru', type=str, required=True, help='Button text (Russian) is required')
banner_parser.add_argument('button_text_tk', type=str, required=True, help='Button text (Turkmen) is required')
banner_parser.add_argument('button_text_en', type=str, required=True, help='Button text (English) is required')
banner_parser.add_argument('button_link', type=str, required=True, help='Button link is required')

# Парсер для валидации данных Project
project_parser = reqparse.RequestParser()
project_parser.add_argument('title_ru', type=str, required=True, help='Title (Russian) is required')
project_parser.add_argument('title_tk', type=str, required=True, help='Title (Turkmen) is required')
project_parser.add_argument('title_en', type=str, required=True, help='Title (English) is required')
project_parser.add_argument('description_ru', type=str, required=True, help='Description (Russian) is required')
project_parser.add_argument('description_tk', type=str, required=True, help='Description (Turkmen) is required')
project_parser.add_argument('description_en', type=str, required=True, help='Description (English) is required')
project_parser.add_argument('background_image_url', type=str, required=True, help='Background image URL is required')
project_parser.add_argument('button_text_ru', type=str, required=True, help='Button text (Russian) is required')
project_parser.add_argument('button_text_tk', type=str, required=True, help='Button text (Turkmen) is required')
project_parser.add_argument('button_text_en', type=str, required=True, help='Button text (English) is required')
project_parser.add_argument('button_link', type=str, required=True, help='Button link is required')
project_parser.add_argument('deliverables_ru', type=str, default=None)
project_parser.add_argument('deliverables_tk', type=str, default=None)
project_parser.add_argument('deliverables_en', type=str, default=None)

# Парсер для валидации данных Blog
blog_parser = reqparse.RequestParser()
blog_parser.add_argument('title_ru', type=str, required=True, help='Title (Russian) is required')
blog_parser.add_argument('title_tk', type=str, required=True, help='Title (Turkmen) is required')
blog_parser.add_argument('title_en', type=str, required=True, help='Title (English) is required')
blog_parser.add_argument('description_ru', type=str, required=True, help='Description (Russian) is required')
blog_parser.add_argument('description_tk', type=str, required=True, help='Description (Turkmen) is required')
blog_parser.add_argument('description_en', type=str, required=True, help='Description (English) is required')
blog_parser.add_argument('image_url', type=str, required=True, help='Image URL is required')
blog_parser.add_argument('additional_images', type=str, default=None)
blog_parser.add_argument('date', type=str, required=True, help='Date is required (YYYY-MM-DD)')
blog_parser.add_argument('read_time', type=str, required=True, help='Read time is required')
blog_parser.add_argument('link', type=str, default='/')

# Ресурс для Banner
class BannerResource(Resource):
    def get(self, banner_id=None):
        locale = request.args.get('lang', 'en')
        if banner_id:
            banner = Banner.query.get_or_404(banner_id)
            return banner.to_dict()
        banners = Banner.query.all()
        return {
            'status': 'success',
            'data': [banner.to_dict() for banner in banners]
        }

    def post(self):
        args = banner_parser.parse_args()
        new_banner = Banner(
            title_ru=args['title_ru'],
            title_tk=args['title_tk'],
            title_en=args['title_en'],
            subtitle_ru=args['subtitle_ru'],
            subtitle_tk=args['subtitle_tk'],
            subtitle_en=args['subtitle_en'],
            image_url=args['image_url'],
            button_text_ru=args['button_text_ru'],
            button_text_tk=args['button_text_tk'],
            button_text_en=args['button_text_en'],
            button_link=args['button_link']
        )
        db.session.add(new_banner)
        db.session.commit()
        return {'message': 'Banner created successfully', 'id': new_banner.id}, '200'

    def put(self, banner_id):
        banner = Banner.query.get_or_404(banner_id)
        args = banner_parser.parse_args()
        banner.title_ru = args['title_ru']
        banner.title_tk = args['title_tk']
        banner.title_en = args['title_en']
        banner.subtitle_ru = args['subtitle_ru']
        banner.subtitle_tk = args['subtitle_tk']
        banner.subtitle_en = args['subtitle_en']
        banner.image_url = args['image_url']
        banner.button_text_ru = args['button_text_ru']
        banner.button_text_tk = args['button_text_tk']
        banner.button_text_en = args['button_text_en']
        banner.button_link = args['button_link']
        db.session.commit()
        return {'message': 'Banner updated successfully'}, '200'

    def delete(self, banner_id):
        banner = Banner.query.get_or_404(banner_id)
        db.session.delete(banner)
        db.session.commit()
        return {'message': 'Banner deleted successfully'}, '200'

# Ресурс для проекта
class ProjectResource(Resource):
    def get(self, project_id=None):
        locale = request.args.get('lang', 'en')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 50)
        category_id = request.args.get('category_id', type=int)

        if project_id:
            project = Project.query.get_or_404(project_id)
            return project.to_dict()

        query = Project.query
        if category_id:
            query = query.join(project_category).filter(project_category.c.category_id == category_id)

        pagination = query.order_by(Project.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        projects = pagination.items  # Убрали скобки, так как items — атрибут

        return {
            'status': 'success',
            'data': [project.to_dict() for project in projects],
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_page': pagination.next_num if pagination.has_next else None,
                'prev_page': pagination.prev_num if pagination.has_prev else None
            }
        }
    def post(self):
        args = project_parser.parse_args()
        new_project = Project(
            title_ru=args['title_ru'],
            title_tk=args['title_tk'],
            title_en=args['title_en'],
            description_ru=args['description_ru'],
            description_tk=args['description_tk'],
            description_en=args['description_en'],
            background_image_url=args['image_url'],
            button_text_ru=args['button_text_ru'],
            button_text_tk=args['button_text_tk'],
            button_text_en=args['button_text_en'],
            button_link=args['link'],
            deliverables_ru=args['deliverables_ru'],
            deliverables_tk=args['deliverables_tk'],
            deliverables_en=args['deliverables_en']
        )
        db.session.add(new_project)
        db.session.commit()
        return {'message': 'Project created successfully', 'id': new_project.id}, '200'

    def put(self, project_id):
        project = Project.query.get_or_404(project_id)
        args = project_parser.parse_args()
        project.title_ru = args['title_ru']
        project.title_tk = args['title_tk']
        project.title_en = args['title_en']
        project.description = args['description_ru']
        project.description_tk = args['description_tk']
        project.description =_en=args['description_en']
        project.background_image_url = args['image_url']
        project.button_text_ru = args['button_text_ru']
        project.button_text_tk = args['button_text_tk']
        project.button_text_en = args['button_text_en']
        project.button_link = args['link']
        project.deliverables_ru = args['deliverables_ru']
        project.deliverables_tk = args['deliverables_tk']
        project.deliverables_en = args['deliverables_en']
        db.session.commit()
        return {'message': 'Project updated successfully'}, '200'

    def delete(self, project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return {'message': 'Project deleted successfully'}, '200'

# Ресурс для Blog
class BlogResource(Resource):
    def get(self, blog_id=None):
        locale = request.args.get('lang', 'en')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 50)  # Максимально 50 элементов

        if blog_id:
            blog = Blog.query.get_or_404(blog_id)
            return blog.to_dict()

        pagination = Blog.query.order_by(Blog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        blogs = pagination.items

        return {
            'status': 'success',
            'data': [blog.to_dict() for blog in blogs],
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_page': pagination.next_num if pagination.has_next else None,
                'prev_page': pagination.prev_num if pagination.has_prev else None
            }
        }

    def post(self):
        from datetime import datetime
        args = blog_parser.parse_args()
        new_blog = Blog(
            title_ru=args['title_ru'],
            title_tk=args['title_tk'],
            title_en=args['title_en'],
            description_ru=args['description_ru'],
            description_tk=args['description_tk'],
            description_en=args['description_en'],
            image_url=args['image_url'],
            additional_images=args['additional_images'],
            date=datetime.strptime(args['date'], '%Y-%m-%d'),
            read_time=args['read_time'],
            link=args['link']
        )
        db.session.add(new_blog)
        db.session.commit()
        return {'message': 'Blog post created successfully', 'id': new_blog.id}, '200'

    def put(self, blog_id):
        from datetime import datetime
        blog = Blog.query.get_or_404(blog_id)
        args = blog_parser.parse_args()
        blog.title_ru = args['title_ru']
        blog.title_tk = args['title_tk']
        blog.title_en = args['title_en']
        blog.description_ru = args['description_ru']
        blog.description_tk = args['description_tk']
        blog.description_en = args['description_en']
        blog.image_url = args['image_url']
        blog.additional_images = args['additional_images']
        blog.date = datetime.strptime(args['date'], '%Y-%m-%d')
        blog.read_time = args['read_time']
        blog.link = args['link']
        db.session.commit()
        return {'message': 'Blog post updated successfully'}, '200'

    def delete(self, blog_id):
        blog = Blog.query.get_or_404(blog_id)
        db.session.delete(blog)
        db.session.commit()
        return {'message': 'Blog post deleted successfully'}, '200'

# Регистрация ресурсов
def init_api(app):
    from app.api import api_bp, api
    app.register_blueprint(api_bp, url_prefix='/api')
    api.add_resource(BannerResource, '/banners', '/banners/<int:banner_id>')
    api.add_resource(ProjectResource, '/projects', '/projects/<int:project_id>')
    api.add_resource(BlogResource, '/blog', '/blog/<int:blog_id>')