from flask import Flask, redirect, url_for, request, has_request_context, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from flask_cors import CORS
from flask_babel import Babel, _
from flask_ckeditor import CKEditor
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
    column_list = ('id', 'title', 'subtitle', 'image_url', 'logo_url', 'button_text', 'button_link', 'created_at')
    form_columns = ('title', 'subtitle', 'image_file', 'logo_file', 'button_text', 'button_link')
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
    column_list = ('id', 'title', 'slug', 'link', 'bg_color', 'description', 'created_at')
    form_columns = ('title', 'slug', 'link', 'bg_color', 'description')

# Project Admin
from app.models.project import Project
class ProjectAdminView(ModelAdminView):
    column_list = ('id', 'title', 'description', 'background_image_url', 'button_text', 'button_link', 'color', 'type', 'created_at')
    form_columns = ('title', 'description', 'background_image_file', 'button_text', 'button_link', 'deliverables', 'color', 'type', 'categories')
    form_extra_fields = {
        'background_image_file': FileUploadField('Background Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.background_image_file.data:
            filename = secure_filename(form.background_image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.background_image_file.data.save(file_path)
            model.background_image_url = f'/Uploads/{filename}'
        if not model.background_image_url and is_created:
            raise ValueError("Background image required")

# Blog Admin
from app.models.blog import Blog
class BlogAdminView(ModelAdminView):
    column_list = ('id', 'title', 'description', 'image_url', 'additional_images', 'date', 'read_time', 'link', 'created_at')
    form_columns = ('title', 'description', 'image_file', 'additional_images_files', 'date', 'read_time', 'link')
    form_extra_fields = {
        'image_file': FileUploadField('Main Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
        'additional_images_files': MultipleFileUploadField('Additional Images', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/Uploads/{filename}'
        if form.additional_images_files.data:
            additional_images = []
            for file in form.additional_images_files.data:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    additional_images.append(f'/Uploads/{filename}')
            model.additional_images = ','.join(additional_images) if additional_images else None
        if not model.image_url and is_created:
            raise ValueError("Main image required")

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

# About Admin (основная информация)
from app.models.about import About, AboutItem
class AboutAdminView(ModelAdminView):
    column_list = ('id', 'title', 'description')
    form_columns = ('title', 'description')

# AboutItem Admin (элементы about.items)
class AboutItemAdminView(ModelAdminView):
    column_list = ('id', 'about_id', 'title', 'description', 'background_image_url', 'button_text', 'button_link', 'color', 'type', 'created_at')
    form_columns = ('about_id', 'title', 'description', 'background_image_file', 'button_text', 'button_link', 'deliverables', 'color', 'type', 'categories', 'created_at')
    form_extra_fields = {
        'background_image_file': FileUploadField('Background Image', base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
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
from app.models.service import Service
class ServiceAdminView(ModelAdminView):
    column_list = ('id', 'content', 'created_at', 'category_id')
    form_columns = ('content', 'category', 'projects', 'blogs')

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
    column_list = ('id', 'title', 'content', 'image_url', 'button_text', 'button_link', 'created_at')
    form_columns = ('title', 'content', 'image_file', 'button_text', 'button_link')
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

def get_locale_from_request():
    if has_request_context():
        lang = request.args.get('lang')
        if lang in ['ru', 'tk', 'en']:
            return lang
        return request.accept_languages.best_match(['ru', 'tk', 'en'], default='en')
    return 'en'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'site.db')
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
    admin.add_view(ModelAdminView(Partner, db.session, name="Partners"))
    admin.add_view(WorkAdminView(Work, db.session, name="Works"))
    admin.add_view(UserAdminView(User, db.session, name="Users"))

    with app.app_context():
        admin.add_link(MenuLink(name=_('Logout'), url='/logout'))

    from app.api.resources import init_api
    init_api(app)

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("All tables created")

            # Пример инициализации данных (минимально, только для теста)
            if not User.query.first():
                admin_user = User(username='admin', is_admin=True)
                admin_user.set_password('admin123')
                db.session.add(admin_user)

            if not Banner.query.first():
                banner = Banner(
                    title="We are IT company specialising in Marketing, Branding design and ERP solutions.",
                    subtitle="Tagma is a dynamic IT company based in Ashgabat, Turkmenistan, specializing in innovative solutions that empower businesses to thrive in the digital age.",
                    image_url="/images/image.png",
                    logo_url="/images/image2.png",
                    button_text="See what we can do",
                    button_link="/services",
                    created_at=datetime(2025, 5, 27, 12, 45, 17)
                )
                db.session.add(banner)

            if not Category.query.first():
                categories = [
                    dict(id=1, title="Graphic Design& Branding", slug="branding-design", link="/services/#branding-design", bg_color="#FAFAFA", description="Property Flow is our unique digital marketing offering created exclusively for property clients.", created_at=datetime(2025, 6, 28, 5, 8, 6)),
                    dict(id=2, title="IT Consulting", slug="it-consulting", link="/services/#it-consulting", bg_color="#F4F4F4", description="Property Flow is our unique digital marketing offering created exclusively for property clients.", created_at=datetime(2025, 6, 28, 5, 8, 6)),
                ]
                for cat in categories:
                    db.session.add(Category(**cat))

            if not Project.query.first():
                category = Category.query.first()
                project = Project(
                    title="Qwatt LED Bulb",
                    description="Tagma’s branding shines through in Qwatt’s identity-bright, bold, and timeless, just like its LEDs. We wraps it in a design that speaks clarity and brilliance.",
                    background_image_url="/images/Mask group0.png",
                    button_text="View project",
                    button_link="/static/images/about_office.jpg",
                    deliverables=None,
                    color="#6d6d6d",
                    type="branding",
                    created_at=datetime(2025, 5, 27, 12, 45, 17)
                )
                if category:
                    project.categories.append(category)
                db.session.add(project)

            if not Blog.query.first():
                blog = Blog(
                    title="Website and Interactive Masterplan",
                    description="We're excited to announce the launch of Wallis Creek, a new community website featuring the innovative...",
                    image_url="/images/image4.png",
                    additional_images=None,
                    date=datetime(2025, 1, 1),
                    read_time="3 min read",
                    link="https://turkmentv.gov.tm",
                    created_at=datetime(2025, 6, 10, 16, 52, 48)
                )
                db.session.add(blog)

            if not Client.query.first():
                client = Client(
                    logo_url="/images/icons/umbrellahover.svg",
                    default_logo="/images/icons/umbrella.svg",
                    created_at=datetime(2025, 5, 27, 12, 45, 17)
                )
                db.session.add(client)

            if not About.query.first():
                about = About(
                    title="About Us",
                    description="Property Flow is our unique digital marketing offering created exclusively for property clients. We build sophisticated, award-winning solutions that encompass four quadrants: discover, design, build and grow."
                )
                db.session.add(about)
                db.session.flush()
                about_item = AboutItem(
                    about_id=about.id,
                    title="Qwatt LED Bulb",
                    description="Tagma’s branding shines through in Qwatt’s identity-bright, bold, and timeless, just like its LEDs. We wraps it in a design that speaks clarity and brilliance.",
                    background_image_url="/images/Mask group0.png",
                    button_text="View project",
                    button_link="/static/images/about_office.jpg",
                    deliverables=None,
                    color="#6d6d6d",
                    type="branding",
                    created_at=datetime(2025, 5, 27, 12, 45, 17)
                )
                db.session.add(about_item)

            if not Work.query.first():
                work = Work(
                    title="Qwatt LED Bulb",
                    description="Tagma’s branding shines through in Qwatt’s identity-bright, bold, and timeless, just like its LEDs. We wraps it in a design that speaks clarity and brilliance.",
                    tags=["Branding", "Design"],
                    main_image="/images/image9.png",
                    content="Ausbuild.com.au is a lead generating, UX focused website that is powered by a creditable tech stack: Salesforce CRM, Heroku and Craft CMS. The site is integrated with Pardot and REA/Domain. And, includes a number of standout features such an interactive Masterplan and Floorplans, ability to Compare/Favourite properties, dynamic content and more. We’re pretty excited to see this project come to life and continue to evolve!",
                    images=["/images/image9.png", "/images/image9.png", "/images/image9.png"],
                    created_at=datetime(2025, 5, 27, 12, 45, 17),
                    bg_color="oklch(79.2% 0.209 151.711)",
                    type="branding"
                )
                db.session.add(work)

            db.session.commit()
            app.logger.info("Initial data created")

        except OperationalError as e:
            app.logger.error(f"Ошибка инициализации данных: {str(e)}")

    return app

if __name__ == '__main__':
    app = create_app()