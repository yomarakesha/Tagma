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
from wtforms import validators, StringField
import errno
import stat
import logging
import tempfile
from flask_admin.form import Select2Widget
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import TextAreaField


db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
ckeditor = CKEditor()
login_manager = LoginManager()

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

from wtforms.fields import SelectField
from wtforms.widgets import Select
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField as BaseQuerySelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField as BaseQuerySelectMultipleField

class CompatibleQuerySelectField(QuerySelectField):
    def iter_choices(self):
        for choice in super().iter_choices():
            yield choice

class CompatibleQuerySelectMultipleField(BaseQuerySelectMultipleField):
    def iter_choices(self):
        for choice in super().iter_choices():
            yield choice[:3]

class PlainSelectField(SelectField):
    widget = Select()
from wtforms import TextAreaField
from app.models.project import Project
from app.utils.image_preview import MultipleImagePreviewField

class ProjectAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'description_ru', 'description_en',
        'main_image', 'bg_color', 'type', 'created_at'
    )
    column_filters = ["categories.title_ru"]

    form_columns = (
        'title_ru', 'title_en', 'description_ru', 'description_en',
        'main_image_file', 'content_ru', 'content_en',
        'tags_ru', 'tags_en', 'images', 'bg_color', 'type', 'categories'
    )
    form_columns += ('images_files', 'existing_images_preview')

    form_extra_fields = {
        'main_image_file': FileUploadField(
            'Main Image',
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        ),
        'images_files': MultipleFileUploadField(
            'Доп. изображения',
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        ),
        'existing_images_preview': MultipleImagePreviewField('Загруженные изображения', existing_images=[]),
    }

    def on_form_prefill(self, form, id):
        project = self.model.query.get(id)
        if not project:
            return

        # Удаление изображения через query-параметр
        remove_image_url = request.args.get('remove_image')
        if remove_image_url and remove_image_url in project.images:
            project.images.remove(remove_image_url)
            try:
                # Удаляем сам файл, если он существует
                abs_path = os.path.join(current_app.root_path, remove_image_url.lstrip('/'))
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            except Exception as e:
                current_app.logger.warning(f"Не удалось удалить файл: {e}")
            db.session.commit()

        # Обновлённый список
        form.existing_images_preview.existing_images = project.images

    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField,
        'deliverables_ru': CKEditorField,
        'deliverables_en': CKEditorField,
        'type': PlainSelectField,
        'categories': CompatibleQuerySelectMultipleField,
    }
    form_args = {
        'type': {
            'choices': [('branding', 'Branding'), ('others', 'Others')],
            'label': 'Тип проекта',
        },
        'categories': {
            'query_factory': lambda: Category.query.order_by(Category.title_ru),
            'get_label': 'title_ru',
            'allow_blank': True,
        }
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        
        # Проверяем существование папки
        if not os.path.exists(upload_folder):
            current_app.logger.error(f"Папка загрузки не существует: {upload_folder}")
            raise ValueError(f"Папка загрузки не существует: {upload_folder}")
        
        current_app.logger.info(f"Путь к папке загрузки: {upload_folder}")
        
        if form.main_image_file.data:
            filename = secure_filename(form.main_image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Сохранение основного изображения в: {file_path}")
            form.main_image_file.data.save(file_path)
            model.main_image = f'/Uploads/{filename}'
        
        if form.images_files.data:
            filenames = []
            for img in form.images_files.data:
                filename = secure_filename(img.filename)
                file_path = os.path.join(upload_folder, filename)
                current_app.logger.info(f"Сохранение дополнительного изображения в: {file_path}")
                img.save(file_path)
                filenames.append(f'/Uploads/{filename}')
            model.images = filenames
# Blog Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from app.models.blog import Blog
from app.utils.file_upload import FileUploadField, MultipleFileUploadField
from werkzeug.utils import secure_filename
import os

class BlogAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'description_ru', 'description_en',
        'image_url', 'date', 'created_at'
    )

    form_extra_fields = {
        'image_file': FileUploadField(
            'Main Image',
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        ),
        'additional_images_files': MultipleFileUploadField(
            'Доп. изображения',
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        )
    }

    form_columns = (
        'title_ru', 'title_en', 'description_ru', 'description_en',
        'image_file', 'additional_images_files', 'date', 'created_at'
    )

    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)

        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            path = os.path.join(upload_folder, filename)
            form.image_file.data.save(path)
            model.image_url = f'/Uploads/{filename}'

        if form.additional_images_files.data:
            filenames = []
            for img in form.additional_images_files.data:
                filename = secure_filename(img.filename)
                path = os.path.join(upload_folder, filename)
                img.save(path)
                filenames.append(f'/Uploads/{filename}')
            model.additional_images = filenames


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

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.background_image_file.data:
            filename = secure_filename(form.background_image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.background_image_file.data.save(file_path)
            model.background_image_url = f'/Uploads/{filename}'

# Service Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from app.models.category import Category

# Используем кастомный класс с совместимостью
class CompatibleQuerySelectField(QuerySelectField):
    def iter_choices(self):
        for choice in super().iter_choices():
            yield choice[:3]
from app.models.project import Project
from app.models.blog import Blog
class ServiceAdminView(ModelAdminView):  # 👈 заменили ModelView на ModelAdminView
    form_columns = ('content_ru', 'content_en', 'category', 'projects', 'blogs')

    form_overrides = {
        'content_ru': CKEditorField,
        'content_en': CKEditorField,
        'category': CompatibleQuerySelectField,
        
    }

    form_args = {
        'category': {
            'query_factory': lambda: Category.query.all(),
            'get_label': lambda c: c.title_ru,
            'allow_blank': False,
        }
    }
    form_overrides.update({
    'projects': CompatibleQuerySelectMultipleField,
    'blogs': CompatibleQuerySelectMultipleField
})

    form_args.update({
        'projects': {
            'query_factory': lambda: Project.query.order_by(Project.title_ru).all(),
            'get_label': 'title_ru',
            'allow_blank': True
        },
        'blogs': {
            'query_factory': lambda: Blog.query.order_by(Blog.title_ru).all(),
            'get_label': 'title_ru',
            'allow_blank': True
        }
    })

    def on_model_change(self, form, model, is_created):
        print("form.category.data:", form.category.data)
        print("type:", type(form.category.data))


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
        self._ensure_upload_folder(upload_folder)
        if form.pdf_file.data:
            filename = secure_filename(form.pdf_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.pdf_file.data.save(file_path)
            model.pdf_file = f'/Uploads/{filename}'
        elif is_created:
            raise ValueError("PDF-файл обязателен")


# User Admin
from wtforms import PasswordField

class UserAdminView(ModelAdminView):
    column_list = ('id', 'username', 'is_admin', 'created_at')
    form_columns = ('username', 'password', 'is_admin')

    form_extra_fields = {
        'password': PasswordField('Пароль')
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)
        elif is_created:
            raise ValueError("Пароль обязателен для нового пользователя")


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
    app.config['UPLOAD_FOLDER'] = os.path.normpath(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Uploads')))
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(__file__), 'translations')
    # ... остальная часть функции create_app остается без изменений ...
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
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.models.contact_request import ContactRequest
    from app.models.partner import Partner
    from app.models.blog import Blog
    from app.models.banner import Banner
    from app.models.category import Category
    from app.models.project import Project
    from app.models.client import Client
    from app.models.about import About, AboutItem
    from app.models.service import Service
    from app.models.portfolio_pdf import PortfolioPDF
    from app.models.contact import Contact
    from app.models.user import User

    admin = Admin(app, index_view=MyAdminIndexView(), template_mode='bootstrap4')

    admin.add_view(BannerAdminView(Banner, db.session, name=_('Banner')))
    admin.add_view(CategoryAdminView(Category, db.session, name=_('Category')))
    admin.add_view(ProjectAdminView(Project, db.session, name=_('Project')))
    admin.add_view(BlogAdminView(Blog, db.session, name=_('Blog')))
    admin.add_view(ClientAdminView(Client, db.session, name=_('Client')))
    admin.add_view(AboutAdminView(About, db.session, name=_('About')))
    # admin.add_view(AboutItemAdminView(AboutItem, db.session, name=_('About Item')))
    admin.add_view(ServiceAdminView(Service, db.session, name=_('Service')))
    admin.add_view(PortfolioPDFAdminView(PortfolioPDF, db.session, name=_('Portfolio PDF')))
    admin.add_view(UserAdminView(User, db.session, name=_('User')))
    admin.add_view(ContactAdminView(Contact, db.session, name=_('Contact')))
    admin.add_view(PartnerAdminView(Partner, db.session, name=_('Partner')))
    admin.add_link(MenuLink(name=_('Go to Website'), url='/'))
    admin.add_link(MenuLink(name=_('Logout'), url='/logout'))

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("База данных инициализирована успешно.")
        except OperationalError as e:
            app.logger.error(f"Ошибка при инициализации базы данных: {str(e)}")

    return app