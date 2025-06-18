from flask_restful import Resource, reqparse, Api
from flask import request, send_file, abort, Blueprint, current_app
from app import db
from app.models.banner import Banner
from app.models.project import Project
from app.models.blog import Blog
from app.models.category import Category, project_category
import io
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime
from fpdf import FPDF

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

# Парсер для загрузки PDF
pdf_parser = reqparse.RequestParser()
pdf_parser.add_argument('pdf', type=FileStorage, location='files', required=True, help='PDF file is required')

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
        return {'message': 'Project created successfully', 'id': new_project.id}, 200

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
        per_page = min(request.args.get('per_page', 5, type=int), 50)

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

# Ресурс для загрузки изображения
class ImageUploadResource(Resource):
    def post(self):
        args = image_parser.parse_args()
        image_file = args['image']

        if not allowed_file(image_file.filename):
            abort(400, description="Invalid file format. Allowed formats: png, jpg, jpeg, gif")

        filename = secure_filename(image_file.filename)
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            current_app.logger.info(f"Created directory: {upload_dir}")

        file_path = os.path.join(upload_dir, filename)
        try:
            image_file.save(file_path)
            current_app.logger.info(f"Image saved at: {file_path}")
        except Exception as e:
            current_app.logger.error(f"Failed to save image at {file_path}: {str(e)}")
            abort(500, description=f"Failed to save image: {str(e)}")

        return {'message': 'Image uploaded successfully', 'filename': filename}, 201

# Ресурс для скачивания изображения
class ImageDownloadResource(Resource):
    def get(self, filename):
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename, mimetype='image/jpeg')
        abort(404, description="Image not found")

# Ресурс для загрузки PDF
class ProjectPDFUploadResource(Resource):
    def post(self, project_id):
        project = Project.query.get_or_404(project_id)
        args = pdf_parser.parse_args()
        pdf_file = args['pdf']

        if not pdf_file.filename.endswith('.pdf'):
            abort(400, description="Invalid file format. Only PDF is allowed")

        filename = secure_filename(pdf_file.filename)
        pdf_dir = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
            current_app.logger.info(f"Created directory: {pdf_dir}")

        file_path = os.path.join(pdf_dir, filename)
        try:
            pdf_file.save(file_path)
            current_app.logger.info(f"PDF saved at: {file_path}")
        except Exception as e:
            current_app.logger.error(f"Failed to save PDF at {file_path}: {str(e)}")
            abort(500, description=f"Failed to save PDF: {str(e)}")

        project.pdf_file = f'/static/uploads/{filename}'
        db.session.commit()
        current_app.logger.info(f"Updated project {project_id} with pdf_file: {project.pdf_file}")
        return {'message': 'PDF uploaded successfully', 'filename': filename, 'pdf_path': project.pdf_file}, 201

# Ресурс для скачивания PDF
class ProjectPDFResource(Resource):
    def get(self, project_id):
        project = Project.query.get_or_404(project_id)
        
        if project.pdf_file and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], project.pdf_file.lstrip('/static/uploads'))):
            return send_file(os.path.join(current_app.config['UPLOAD_FOLDER'], project.pdf_file.lstrip('/static/uploads')),
                            as_attachment=True,
                            download_name=os.path.basename(project.pdf_file),
                            mimetype='application/pdf')

        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.add_font('DejaVu', '', 'app/static/fonts/DejaVuSans.ttf', uni=True)
            pdf.set_font('DejaVu', size=12)
        except Exception as e:
            pdf.set_font('Arial', size=12)
            current_app.logger.error(f"Failed to load DejaVu font: {e}")

        pdf.cell(200, 10, txt=f"Project Details - ID: {project_id}", ln=True, align="C")
        pdf.ln(10)

        pdf.cell(200, 10, txt=f"Title (English): {project.title_en}", ln=True)
        pdf.cell(200, 10, txt=f"Название (Русский): {project.title_ru}", ln=True)
        pdf.cell(200, 10, txt=f"At (Türkmen): {project.title_tk}", ln=True)
        pdf.ln(10)

        pdf.multi_cell(0, 10, txt=f"Description (English): {project.description_en}", align='L')
        pdf.multi_cell(0, 10, txt=f"Описание (Русский): {project.description_ru}", align='L')
        pdf.multi_cell(0, 10, txt=f"Bellik (Türkmen): {project.description_tk}", align='L')
        pdf.ln(10)

        pdf.cell(200, 10, txt="Categories:", ln=True)
        for cat in project.categories:
            pdf.cell(200, 10, txt=f"- {cat.name_en}", ln=True)
        pdf.ln(10)

        pdf.cell(200, 10, txt=f"Image URL: {project.background_image_url}", ln=True)

        pdf_file = io.BytesIO()
        pdf.output(pdf_file)
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
    api.add_resource(ProjectPDFUploadResource, '/project/<int:project_id>/upload-pdf')

# Функция для проверки разрешенных расширений
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS