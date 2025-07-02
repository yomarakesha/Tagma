from flask import Flask, redirect, url_for, request, has_request_context, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from flask_cors import CORS
from flask_babel import Babel, _
from flask_ckeditor import CKEditor, CKEditorField
import os
from datetime import datetime
from sqlalchemy.exc import OperationalError
from werkzeug.utils import secure_filename
from app.utils.file_upload import FileUploadField, MultipleFileUploadField
from wtforms import validators, PasswordField
import errno
import stat
import logging
import tempfile

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
ckeditor = CKEditor()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login'))

class ModelAdminView(ModelView):
    extra_js = [
        '//cdn.ckeditor.com/4.16.2/standard/ckeditor.js'
    ]
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def _ensure_upload_folder(self, folder_path):
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
                current_app.logger.info(f"Создана папка для загрузки: {folder_path}")
            except OSError as e:
                current_app.logger.error(f"Не удалось создать папку для загрузки {folder_path}: {str(e)}")
                temp_dir = tempfile.gettempdir()
                current_app.config['UPLOAD_FOLDER'] = temp_dir
                current_app.logger.warning(f"Переключение на временную папку: {temp_dir}")
                os.makedirs(temp_dir, exist_ok=True)
        if not os.access(folder_path, os.W_OK):
            current_app.logger.error(f"Нет прав на запись в {folder_path}. Пытаемся предоставить доступ.")
            try:
                os.chmod(folder_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                current_app.logger.info(f"Предоставлены права на запись в {folder_path}")
            except OSError as e:
                current_app.logger.error(f"Не удалось предоставить права на запись в {folder_path}: {str(e)}")
                raise ValueError(f"Нет прав на запись в папку загрузки: {folder_path}")

# Banner Admin
from app.models.banner import Banner
class BannerAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'subtitle_ru', 'subtitle_en',
        'image_url', 'logo_url', 'button_text_ru', 'button_text_en', 'button_link', 'created_at'
    )
    form_columns = (
        'title_ru', 'title_en', 'subtitle_ru', 'subtitle_en',
        'image_file', 'logo_file', 'button_text_ru', 'button_text_en', 'button_link'
    )
    form_extra_fields = {
        'image_file': FileUploadField('Banner Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
        'logo_file': FileUploadField('Logo', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/Uploads/{filename}'
        if form.logo_file.data:
            filename = secure_filename(form.logo_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.logo_file.data.save(file_path)
            model.logo_url = f'/Uploads/{filename}'
        if not model.image_url and is_created:
            raise ValueError("Banner image required")

# Category Admin
from app.models.category import Category
class CategoryAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_en', 'slug', 'link', 'bg_color', 'description_ru', 'description_en', 'created_at')
    form_columns = ('title_ru', 'title_en', 'slug', 'link', 'bg_color', 'description_ru', 'description_en')
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField
    }

# Project Admin
from app.models.project import Project
class ProjectAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'description_ru', 'description_en',
        'background_image_url', 'button_text_ru', 'button_text_en', 'button_link',
        'deliverables_ru', 'deliverables_en', 'color', 'type', 'created_at'
    )
    form_columns = (
        'title_ru', 'title_en', 'description_ru', 'description_en',
        'background_image_file', 'button_text_ru', 'button_text_en', 'button_link',
        'deliverables_ru', 'deliverables_en', 'color', 'type', 'categories'
    )
    form_extra_fields = {
        'background_image_file': FileUploadField('Background Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
    }
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField,
        'deliverables_ru': CKEditorField,
        'deliverables_en': CKEditorField
    }

# Blog Admin
from app.models.blog import Blog
class BlogAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'description_ru', 'description_en',
        'image_url', 'date', 'created_at'
    )
    form_columns = (
        'title_ru', 'title_en', 'description_ru', 'description_en',
        'image_file', 'date'
    )
    form_extra_fields = {
        'image_file': FileUploadField(
            'Main Image',
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        )
    }
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/Uploads/{filename}'

# Client Admin
from app.models.client import Client
class ClientAdminView(ModelAdminView):
    column_list = ('id', 'logo_url', 'default_logo', 'created_at')
    form_columns = ('logo_file', 'default_logo_file')
    form_extra_fields = {
        'logo_file': FileUploadField('Client Logo', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
        'default_logo_file': FileUploadField('Default Logo', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.logo_file.data:
            filename = secure_filename(form.logo_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.logo_file.data.save(file_path)
            model.logo_url = f'/Uploads/{filename}'
        if form.default_logo_file.data:
            filename = secure_filename(form.default_logo_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.default_logo_file.data.save(file_path)
            model.default_logo = f'/Uploads/{filename}'
        if not model.logo_url and is_created:
            raise ValueError("Client logo required")

# About Admin
from app.models.about import About, AboutItem
class AboutAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_en', 'description_ru', 'description_en')
    form_columns = ('title_ru', 'title_en', 'description_ru', 'description_en')
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField
    }

class AboutItemAdminView(ModelAdminView):
    column_list = (
        'id', 'about_id', 'title_ru', 'title_en', 'description_ru', 'description_en',
        'background_image_url', 'button_text_ru', 'button_text_en', 'button_link',
        'deliverables_ru', 'deliverables_en', 'color', 'type', 'created_at'
    )
    form_columns = (
        'about_id', 'title_ru', 'title_en', 'description_ru', 'description_en',
        'background_image_file', 'button_text_ru', 'button_text_en', 'button_link',
        'deliverables_ru', 'deliverables_en', 'color', 'type', 'categories', 'created_at'
    )
    form_extra_fields = {
        'background_image_file': FileUploadField('Background Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
    }
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField,
        'deliverables_ru': CKEditorField,
        'deliverables_en': CKEditorField
    }

# Service Admin
from app.models.service import Service
class ServiceAdminView(ModelAdminView):
    column_list = ('id', 'content_ru', 'content_en', 'created_at', 'category_id')
    form_columns = ('content_ru', 'content_en', 'category', 'projects', 'blogs')
    form_overrides = {
        'content_ru': CKEditorField,
        'content_en': CKEditorField
    }

# Portfolio PDF Admin
from app.models.portfolio_pdf import PortfolioPDF
class PortfolioPDFAdminView(ModelAdminView):
    form_overrides = {
        'pdf_file': FileUploadField
    }
    form_args = {
        'pdf_file': {
            'label': 'PDF-файл',
            'base_path': lambda: current_app.config['UPLOAD_FOLDER'],
            'allowed_extensions': {'pdf'},
            'validators': [validators.DataRequired()]
        }
    }
    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if form.pdf_file.data:
            filename = secure_filename(form.pdf_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.pdf_file.data.save(file_path)
            model.pdf_file = f'/Uploads/{filename}'
        elif is_created:
            raise ValueError("PDF-файл обязателен")

# Work Admin
from app.models.work import Work
class WorkAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'content_ru', 'content_en',
        'image_url', 'button_text_ru', 'button_text_en', 'button_link', 'created_at'
    )
    form_columns = (
        'title_ru', 'title_en', 'content_ru', 'content_en',
        'image_file', 'button_text_ru', 'button_text_en', 'button_link'
    )
    form_extra_fields = {
        'image_file': FileUploadField('Work Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/Uploads/{filename}'
        if not model.image_url and is_created:
            raise ValueError("Work image required")

# User Admin
from app.models.user import User
class UserAdminView(ModelAdminView):
    column_list = ('id', 'username', 'is_admin', 'created_at')
    form_columns = ('username', 'password', 'is_admin')
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

# Contact Admin
from app.models.contact import Contact
class ContactAdminView(ModelAdminView):
    column_list = ('id', 'phone', 'address_ru', 'address_tk', 'address_en', 'email', 'social_media', 'created_at')
    form_columns = ('phone', 'address_ru', 'address_tk', 'address_en', 'email', 'social_media')

# Partner Admin
from app.models.partner import Partner
class PartnerAdminView(ModelAdminView):
    column_list = ('id', 'name_ru', 'name_en', 'logo_url', 'description_ru', 'description_en', 'created_at')
    form_columns = ('name_ru', 'name_en', 'logo_file', 'description_ru', 'description_en')
    form_extra_fields = {
        'logo_file': FileUploadField(
            'Logo',
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        )
    }
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.logo_file.data:
            filename = secure_filename(form.logo_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.logo_file.data.save(file_path)
            model.logo_url = f'/Uploads/{filename}'
        if not model.logo_url and is_created:
            raise ValueError("Logo image required")

def get_locale_from_request():
    if has_request_context():
        lang = request.args.get('lang')
        if lang in ['ru', 'tk', 'en']:
            return lang
        return request.accept_languages.best_match(['ru', 'tk', 'en'], default='en')
    return 'en'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'site.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Uploads'))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(__file__), 'translations')

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder, exist_ok=True)
            app.logger.info(f"Создана папка для загрузки: {upload_folder}")
        except OSError as e:
            app.logger.error(f"Не удалось создать папку для загрузки {upload_folder}: {str(e)}")
            temp_dir = tempfile.gettempdir()
            app.config['UPLOAD_FOLDER'] = temp_dir
            app.logger.warning(f"Переключение на временную папку: {temp_dir}")
            os.makedirs(temp_dir, exist_ok=True)
    if not os.access(upload_folder, os.W_OK):
        app.logger.error(f"Нет прав на запись в {upload_folder}. Пытаемся предоставить доступ.")
        try:
            os.chmod(upload_folder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            app.logger.info(f"Предоставлены права на запись для {upload_folder}")
        except OSError as e:
            app.logger.error(f"Не удалось предоставить права на запись для {upload_folder}: {str(e)}")
            raise ValueError(f"Нет прав на запись в папку для загрузки: {upload_folder}")

    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/static/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale_from_request)
    ckeditor.init_app(app)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.models.contact_request import ContactRequest
    from app.models.partner import Partner
    from app.models.blog import Blog
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3', index_view=MyAdminIndexView())
    admin.add_view(BannerAdminView(Banner, db.session))
    admin.add_view(ProjectAdminView(Project, db.session))
    admin.add_view(CategoryAdminView(Category, db.session))
    admin.add_view(BlogAdminView(Blog, db.session))
    admin.add_view(ClientAdminView(Client, db.session))
    admin.add_view(ServiceAdminView(Service, db.session))
    admin.add_view(AboutAdminView(About, db.session))
    admin.add_view(AboutItemAdminView(AboutItem, db.session, name="About Items"))
    admin.add_view(PortfolioPDFAdminView(PortfolioPDF, db.session, name="Company Portfolio PDF"))
    admin.add_view(ModelAdminView(ContactRequest, db.session, name="Contact Requests"))
    admin.add_view(PartnerAdminView(Partner, db.session, name="Partners"))
    admin.add_view(WorkAdminView(Work, db.session, name="Works"))
    admin.add_view(UserAdminView(User, db.session, name="Users"))
    # admin.add_view(ContactAdminView(Contact, db.session, name="Контакты"))  # Удалено из админки

    with app.app_context():
        admin.add_link(MenuLink(name=_('Logout'), url='/logout'))

    from app.api.resources import init_api
    init_api(app)

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("All tables created")
        except OperationalError as e:
            app.logger.error(f"Ошибка инициализации данных: {str(e)}")

    return app

if __name__ == '__main__':
    app =create_app()