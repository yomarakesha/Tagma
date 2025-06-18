from flask_restful import Resource, reqparse, Api
from flask import request, send_file, abort, Blueprint, current_app
from app import db, create_app
from app.models.banner import Banner
from app.models.project import Project
from app.models.blog import Blog
from app.models.category import Category, project_category
import io
import subprocess
import os
import sys
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime

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

# Парсер для загрузки изображения
image_parser = reqparse.RequestParser()
image_parser.add_argument('image', type=FileStorage, location='files', required=True, help='Image file is required')

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
        return {'message': 'Banner created successfully', 'id': new_banner.id}, 200

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
        return {'message': 'Banner updated successfully'}, 200

    def delete(self, banner_id):
        banner = Banner.query.get_or_404(banner_id)
        db.session.delete(banner)
        db.session.commit()
        return {'message': 'Banner deleted successfully'}, 200

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
        projects = pagination.items

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
            background_image_url=args['background_image_url'],
            button_text_ru=args['button_text_ru'],
            button_text_tk=args['button_text_tk'],
            button_text_en=args['button_text_en'],
            button_link=args['button_link'],
            deliverables_ru=args['deliverables_ru'],
            deliverables_tk=args['deliverables_tk'],
            deliverables_en=args['deliverables_en']
        )
        db.session.add(new_project)
        db.session.commit()
        return {'message': 'Project created successfully', 'id': new_banner.id}, 200

    def put(self, project_id):
        project = Project.query.get_or_404(project_id)
        args = project_parser.parse_args()
        project.title_ru = args['title_ru']
        project.title_tk = args['title_tk']
        project.title_en = args['title_en']
        project.description_ru = args['description_ru']
        project.description_tk = args['description_tk']
        project.description_en = args['description_en']
        project.background_image_url = args['background_image_url']
        project.button_text_ru = args['button_text_ru']
        project.button_text_tk = args['button_text_tk']
        project.button_text_en = args['button_text_en']
        project.button_link = args['button_link']
        project.deliverables_ru = args['deliverables_ru']
        project.deliverables_tk = args['deliverables_tk']
        project.deliverables_en = args['deliverables_en']
        db.session.commit()
        return {'message': 'Project updated successfully'}, 200

    def delete(self, project_id):
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        return {'message': 'Project deleted successfully'}, 200

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
        return {'message': 'Blog post created successfully', 'id': new_blog.id}, 200

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
        return {'message': 'Blog post updated successfully'}, 200

    def delete(self, blog_id):
        blog = Blog.query.get_or_404(blog_id)
        db.session.delete(blog)
        db.session.commit()
        return {'message': 'Blog post deleted successfully'}, 200

# Новый ресурс для загрузки изображения
class ImageUploadResource(Resource):
    def post(self):
        args = image_parser.parse_args()
        image_file = args['image']

        # Проверка расширения файла
        if not allowed_file(image_file.filename):
            abort(400, description="Invalid file format. Allowed formats: png, jpg, jpeg, gif")

        # Безопасное имя файла
        filename = secure_filename(image_file.filename)
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Сохранение файла
        file_path = os.path.join(upload_dir, filename)
        image_file.save(file_path)

        return {'message': 'Image uploaded successfully', 'filename': filename}, 201

# Новый ресурс для скачивания изображения
class ImageDownloadResource(Resource):
    def get(self, filename):
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename, mimetype='image/jpeg')  # MIME-type можно настроить
        abort(404, description="Image not found")

# Новый ресурс для скачивания PDF
class ProjectPDFResource(Resource):
    def get(self, project_id):
        project = Project.query.get_or_404(project_id)
        
        # Проверка доступности latexmk
        latexmk_path = 'latexmk'  # По умолчанию предполагаем, что в PATH
        if os.name == 'nt':  # Windows
            # Попробуем найти latexmk в стандартной директории TeX Live
            possible_paths = [
                r'C:\texlive\2024\bin\win32\latexmk.exe',
                r'C:\texlive\2023\bin\win32\latexmk.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    latexmk_path = path
                    break
        
        if not any(os.access(latexmk_path, os.X_OK) or os.path.exists(latexmk_path)):
            abort(500, description="latexmk is not installed or not found in PATH. Please install TeX Live and add it to your system PATH.")

        # Генерация LaTeX-кода
        latex_content = f"""
        \\documentclass[a4paper]{{article}}
        \\usepackage[utf8]{{inputenc}}
        \\usepackage[russian, turkmen, english]{{babel}}
        \\usepackage{{geometry}}
        \\geometry{{a4paper, margin=1in}}
        \\usepackage{{graphicx}}

        \\begin{{document}}

        \\section*{{Project Details}}
        \\selectlanguage{{english}}
        \\textbf{{Title:}} {project.title_en}
        \\selectlanguage{{russian}}
        \\textbf{{Название:}} {project.title_ru}
        \\selectlanguage{{turkmen}}
        \\textbf{{At:}} {project.title_tk}

        \\textbf{{Description (English):}} {project.description_en}
        \\textbf{{Описание (Русский):}} {project.description_ru}
        \\textbf{{Bellik (Türkmen):}} {project.description_tk}

        \\textbf{{Categories:}}
        \\begin{{itemize}}
        {''.join([f'\\item {cat.name_en}' for cat in project.categories])}
        \\end{{itemize}}

        \\textbf{{Image URL:}} {project.background_image_url}

        \\end{{document}}
        """

        # Сохранение LaTeX в временный файл
        latex_file = io.StringIO()
        latex_file.write(latex_content)
        latex_file.seek(0)

        # Генерация PDF с помощью latexmk
        pdf_file = io.BytesIO()
        try:
            process = subprocess.run([latexmk_path, '-pdf', '-output-format=pdf', '-jobname=project_{project_id}'],
                                  input=latex_file.read().encode(),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True,
                                  check=True)
            pdf_file.write(process.stdout.encode())
        except subprocess.CalledProcessError as e:
            abort(500, description=f"Failed to generate PDF: {e.stderr}")
        except FileNotFoundError:
            abort(500, description="latexmk executable not found. Ensure TeX Live is installed and PATH is configured.")

        pdf_file.seek(0)
        return send_file(pdf_file,
                        as_attachment=True,
                        download_name=f'project_{project_id}.pdf',
                        mimetype='application/pdf')

# Регистрация ресурсов
def init_api(app):
    from flask_restful import Api
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api = Api(api_bp)
    app.register_blueprint(api_bp)
    api.add_resource(BannerResource, '/banners', '/banners/<int:banner_id>')
    api.add_resource(ProjectResource, '/projects', '/projects/<int:project_id>')
    api.add_resource(BlogResource, '/blog', '/blog/<int:blog_id>')
    api.add_resource(ProjectPDFResource, '/project/<int:project_id>/download-pdf')
    api.add_resource(ImageUploadResource, '/upload-image')
    api.add_resource(ImageDownloadResource, '/download-image/<string:filename>')

# Функция для проверки разрешенных расширений (из __init__.py)
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS