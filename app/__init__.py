from flask import Flask, redirect, url_for, request, has_request_context
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from flask_cors import CORS
from flask_babel import Babel, _, get_locale
import os
from datetime import datetime
from sqlalchemy.exc import OperationalError
from werkzeug.utils import secure_filename
from app.utils.file_upload import FileUploadField, MultipleFileUploadField
from wtforms import TextAreaField
from wtforms.fields import SelectMultipleField
from flask_admin.form import Select2Widget
from flask import current_app
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()

# Конфигурация загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Кастомное поле для Quill Editor
class QuillTextAreaField(TextAreaField):
    def __init__(self, label=None, validators=None, **kwargs):
        super(QuillTextAreaField, self).__init__(label, validators, **kwargs)

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login'))

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return self.inaccessible_callback(name, **kwargs)

class ModelAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class BlogAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'date', 'read_time', 'image_url', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'description_ru', 'description_tk', 'description_en', 'image_file', 'additional_images_files', 'date', 'read_time', 'link')
    form_extra_fields = {
        'image_file': FileUploadField(_('Main Image'), base_path=UPLOAD_FOLDER, allowed_extensions=ALLOWED_EXTENSIONS),
        'additional_images_files': MultipleFileUploadField(_('Additional Images'), base_path=UPLOAD_FOLDER, allowed_extensions=ALLOWED_EXTENSIONS),
        'description_ru': QuillTextAreaField(_('Description (Russian)')),
        'description_tk': QuillTextAreaField(_('Description (Turkmen)')),
        'description_en': QuillTextAreaField(_('Description (English)'))
    }
    form_widget_args = {
        'description_ru': {'class': 'quill-editor'},
        'description_tk': {'class': 'quill-editor'},
        'description_en': {'class': 'quill-editor'}
    }
    edit_template = 'admin/blog_edit.html'

    def on_model_change(self, form, model, is_created):
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/static/uploads/{filename}'
        if not model.image_url:
            raise ValueError(_("Main image is required"))

class BannerAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'image_url', 'button_text_ru', 'button_text_tk', 'button_text_en', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'subtitle_ru', 'subtitle_tk', 'subtitle_en', 'image_file', 'button_text_ru', 'button_text_tk', 'button_text_en', 'button_link')
    form_extra_fields = {
        'image_file': FileUploadField(_('Banner Image'), base_path=UPLOAD_FOLDER, allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/static/uploads/{filename}'
        if not model.image_url:
            raise ValueError(_("Banner image is required"))

class ProjectAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'background_image_url', 'button_text_ru', 'button_text_tk', 'button_text_en', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'description_ru', 'description_tk', 'description_en', 'background_image_file', 'button_text_ru', 'button_text_tk', 'button_text_en', 'button_link', 'deliverables_ru', 'deliverables_tk', 'deliverables_en', 'categories')
    form_extra_fields = {
        'background_image_file': FileUploadField(_('Background Image'), base_path=UPLOAD_FOLDER, allowed_extensions=ALLOWED_EXTENSIONS),
        'description_ru': QuillTextAreaField(_('Description (Russian)')),
        'description_tk': QuillTextAreaField(_('Description (Turkmen)')),
        'description_en': QuillTextAreaField(_('Description (English)')),
        'deliverables_ru': QuillTextAreaField(_('Deliverables (Russian)')),
        'deliverables_tk': QuillTextAreaField(_('Deliverables (Turkmen)')),
        'deliverables_en': QuillTextAreaField(_('Deliverables (English)')),
        'categories': SelectMultipleField(
            _('Categories'),
            coerce=int,
            widget=Select2Widget(multiple=True)
        )
    }
    form_widget_args = {
        'description_ru': {'class': 'quill-editor'},
        'description_tk': {'class': 'quill-editor'},
        'description_en': {'class': 'quill-editor'},
        'deliverables_ru': {'class': 'quill-editor'},
        'deliverables_tk': {'class': 'quill-editor'},
        'deliverables_en': {'class': 'quill-editor'}
    }

    def get_form(self):
        form = super().get_form()
        return form

    def create_form(self):
        form = super().create_form()
        from app.models.category import Category  # type: ignore
        with current_app.app_context():  # Используем current_app
            form.categories.choices = [(str(c.id), c.__str__()) for c in db.session.query(Category).all()]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        from app.models.category import Category  # type: ignore
        with current_app.app_context():  # Используем current_app
            form.categories.choices = [(str(c.id), c.__str__()) for c in db.session.query(Category).all()]
        return form

    def on_model_change(self, form, model, is_created):
        if form.background_image_file.data:
            filename = secure_filename(form.background_image_file.data.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            form.background_image_file.data.save(file_path)
            model.background_image_url = f'/static/uploads/{filename}'
        if not model.background_image_url:
            raise ValueError(_("Background image is required"))
class ClientAdminView(ModelAdminView):
    column_list = ('id', 'logo_url', 'created_at')
    form_columns = ('logo_file',)
    form_extra_fields = {
        'logo_file': FileUploadField(_('Client Logo'), base_path=UPLOAD_FOLDER, allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        if form.logo_file.data:
            filename = secure_filename(form.logo_file.data.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            form.logo_file.data.save(file_path)
            model.logo_url = f'/static/uploads/{filename}'
        if not model.logo_url:
            raise ValueError(_("Client logo is required"))

class AboutAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'image_url', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'subtitle_ru', 'subtitle_tk', 'subtitle_en', 'description1_ru', 'description1_tk', 'description1_en', 'description2_ru', 'description2_tk', 'description2_en', 'image_file')
    form_extra_fields = {
        'image_file': FileUploadField(_('Page Image'), base_path=UPLOAD_FOLDER, allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            form.image_file.data.save(file_path)
            model.image_url = f'/static/uploads/{filename}'
        if not model.image_url:
            raise ValueError(_("Page image is required"))

class UserAdminView(ModelAdminView):
    column_list = ('id', 'username', 'email', 'is_admin', 'created_at')
    form_columns = ('username', 'email', 'is_admin')

class CategoryAdminView(ModelAdminView):
    column_list = ('id', 'name_ru', 'name_tk', 'name_en', 'created_at')
    form_columns = ('name_ru', 'name_tk', 'name_en')

class ServiceAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'button_text_ru', 'button_text_tk', 'button_text_en', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'subtitles_ru', 'subtitles_tk', 'subtitles_en', 'button_text_ru', 'button_text_tk', 'button_text_en', 'button_link')

class ReviewAdminView(ModelAdminView):
    column_list = ('id', 'content_ru', 'content_tk', 'content_en', 'author_ru', 'author_tk', 'author_en', 'project_id', 'created_at')
    form_columns = ('content_ru', 'content_tk', 'content_en', 'author_ru', 'author_tk', 'author_en', 'project')

class ContactAdminView(ModelAdminView):
    column_list = ('id', 'phone', 'address_ru', 'address_tk', 'address_en', 'email', 'social_media', 'created_at')
    form_columns = ('phone', 'address_ru', 'address_tk', 'address_en', 'email', 'social_media')

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
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(__file__), 'translations')

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/static/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale_from_request)

    app.jinja_env.globals.update(get_locale=get_locale)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3', index_view=MyAdminIndexView())
    from app.models.banner import Banner
    from app.models.project import Project
    from app.models.category import Category
    from app.models.blog import Blog
    from app.models.client import Client
    from app.models.service import Service
    from app.models.review import Review
    from app.models.contact import Contact
    from app.models.about import About

    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(BannerAdminView(Banner, db.session))
    admin.add_view(ProjectAdminView(Project, db.session))
    admin.add_view(CategoryAdminView(Category, db.session))
    admin.add_view(BlogAdminView(Blog, db.session))
    admin.add_view(ClientAdminView(Client, db.session))
    admin.add_view(ServiceAdminView(Service, db.session))
    admin.add_view(ReviewAdminView(Review, db.session))
    admin.add_view(ContactAdminView(Contact, db.session))
    admin.add_view(AboutAdminView(About, db.session))

    with app.app_context():
        admin.add_link(MenuLink(name=_('Logout'), url='/logout'))

    from app.api.resources import init_api
    init_api(app)

    with app.app_context():
        try:
            if not User.query.first():
                admin_user = User(username='admin', email='admin@example.com', is_admin=True)
                admin_user.set_password('admin123')
                db.session.add(admin_user)

            if not Banner.query.first():
                banner = Banner(
                    title_ru='МЫ ДЕЛАЕМ ЭТО',
                    title_tk='BIZ BU EDÝÄRIS',
                    title_en='WE MAKE IT HAPPEN',
                    subtitle_ru='Мы IT-компания, специализирующаяся на маркетинге, брендинге и ERP-решениях',
                    subtitle_tk='Biz marketing, brending we ERP çözgütlerinde ýöriteleşen IT kompaniýasy',
                    subtitle_en='We are IT company specialising in Marketing, Branding design and ERP solutions',
                    image_url='/static/images/banner.jpg',
                    button_text_ru='Посмотрите, что мы можем сделать',
                    button_text_tk='Biziň näme edip biljekdigimizi görüň',
                    button_text_en='See what we can do',
                    button_link='/services'
                )
                db.session.add(banner)

            categories = [
                ('Дизайн брендинга', 'Brending dizaýny', 'Branding Design'),
                ('ИТ-консультации', 'IT maslahat berişlik', 'IT Consulting'),
                ('Решения для инженерных заводов', 'Zawod inženerçilik çözgütleri', 'Factory Engineering Solutions'),
                ('Промышленные ИТ', 'Senagat IT', 'Industrial IT')
            ]
            for name_ru, name_tk, name_en in categories:
                if not Category.query.filter_by(name_en=name_en).first():
                    db.session.add(Category(name_ru=name_ru, name_tk=name_tk, name_en=name_en))

            if not Project.query.first():
                branding = Category.query.filter_by(name_en='Branding Design').first()
                project = Project(
                    title_ru='Лампа Qwatt LED',
                    title_tk='Qwatt LED çyrasy',
                    title_en='Qwatt LED Bulb',
                    description_ru='Брендинг Tagma сияет в идентичности Qwatt — яркий, смелый и вечный, как её светодиоды.',
                    description_tk='Tagmanyň brendingi Qwatt-yň şahsyýetinde ýalpyldawuk — ýagty, batyr we öçmejek, ýaly LED-ler.',
                    description_en="Tagma's Branding Shines Through In Qwatt's identity-Bright, Bold, And Timeless, Just Like its LEDs.",
                    background_image_url='/static/images/qwatt_lamp.jpg',
                    button_text_ru='Посмотреть проект',
                    button_text_tk='Tasar görmek',
                    button_text_en='View project',
                    button_link='/project/qwatt'
                )
                if branding:
                    project.categories.append(branding)
                db.session.add(project)

            if not Project.query.filter_by(title_en='A Digital Transformation').first():
                it_consulting = Category.query.filter_by(name_en='IT Consulting').first()
                deliverables = (
                    "Digital Discovery (Site Architecture/Site Map)\n"
                    "Wireframes\n"
                    "Website Design - Desktop And Mobile\n"
                    "Digital Brand Extension - Formatting Style Sheet\n"
                    "Website Development And Implementation\n"
                    "CMS: Craft\n"
                    "Third-Party Integrations - Salesforce CRM And Pardot\n"
                    "Marketing Assets: PDF Generation, Email (Transactional And Campaign) Templates Etc.\n"
                    "Major And Minor Website Features E.g. Interactive Masterplan, Interactive Home Options Floorplan, Etc.\n"
                    "Integration With REA And Domain"
                )
                project = Project(
                    title_ru='Цифровая трансформация',
                    title_tk='Sanly özgertme',
                    title_en='A Digital Transformation',
                    description_ru='Работая с командой Ausbuild, мы гордимся тем, что достигли цели проекта...',
                    description_tk='Ausbuild topary bilen bilelikde, tasaryň maksadyna ýetendigimizden buýsanýarys...',
                    description_en="Working alongside the Ausbuild team, we are extremely proud to have delivered on the project goal...",
                    background_image_url='/static/images/digital_transformation.jpg',
                    button_text_ru='Посмотреть проект',
                    button_text_tk='Tasar görmek',
                    button_text_en='View project',
                    button_link='/project/digital',
                    deliverables_ru=deliverables,
                    deliverables_tk=deliverables,
                    deliverables_en=deliverables
                )
                if it_consulting:
                    project.categories.append(it_consulting)
                db.session.add(project)

            if not Review.query.first():
                project = Project.query.filter_by(title_en='Qwatt LED Bulb').first()
                if project:
                    review = Review(
                        content_ru='Нам понравилось всё, что мы достигли с вами в этом году...',
                        content_tk='Bu ýyl siziň bilen gazananlarymyzyň hemmesi bize ýarady...',
                        content_en="We've loved all we've achieved with you this year...",
                        author_ru='Трейси Аткинс | Директор — Австралия и Тихоокеанский регион в Forbes Global Properties',
                        author_tk='Treýsi Atkins | Awstraliýa we Pacific ýurtlary boýunça direktor Forbes Global Properties',
                        author_en='Tracey Atkins | Director - Australia Pacific at Forbes Global Properties',
                        project=project
                    )
                    db.session.add(review)

            existing_blogs = Blog.query.filter_by(title_en='Website and Interactive Masterplan').count()
            if existing_blogs < 5:
                for i in range(existing_blogs + 1, 6):
                    blog = Blog(
                        title_ru='Веб-сайт и интерактивный мастер-план',
                        title_tk='Web sahypasy we interaktiw master plan',
                        title_en='Website and Interactive Masterplan',
                        date=datetime(2024, 6, 12),
                        read_time='3 min read',
                        image_url=f'/static/images/masterplan{i}.jpg',
                        link='/',
                        description_ru='Мы рады объявить о запуске Wallis Creek...',
                        description_tk='Wallis Creek-iň açylyşyndan buýsanýarys...',
                        description_en="We're excited to announce the launch of Wallis Creek...",
                        additional_images=None
                    )
                    db.session.add(blog)

            if not Client.query.first():
                client = Client(logo_url='/static/images/hues.png')
                db.session.add(client)

            services = [
                ('ИТ-консультации', 'IT maslahat berişlik', 'IT Consulting', 'Инфраструктура технологий, Экспертные консультации, Кибербезопасность, Оптимизация систем', 'Tehnologiýa infrastruktura, Bilermen maslahat, Kiberhowpsuzlyk, Ulgam optimizasiýa', 'Technology infrastructure, Expert consulting, Cybersecurity, System Optimization', '/services/#it-consulting'),
                ('Дизайн брендинга', 'Brending dizaýny', 'Branding Design', 'Дизайн логотипов, Бренд-идентичность, Дизайн упаковки, Креативное руководство', 'Logotip dizaýny, Brend şahsyýeti, Gap-gaç dizaýny, Döredijilik ýolbaşçylygy', 'Logo design, Brand identity, Packaging design, Creative direction', '/services/#branding-design'),
                ('ERP-решения', 'ERP çözgütleri', 'ERP Solutions', 'Внедрение ERP, Разработка кастомных ERP, Интеграция систем, Поддержка ERP', 'ERP ornaşdyrmak, Şahsy ERP işläp düzmek, Ulgam integrasiýasy, ERP goldawy', 'ERP implementation, Custom ERP development, System integration, ERP support', '/services/#erp-solutions')
            ]
            for title_ru, title_tk, title_en, subtitles_ru, subtitles_tk, subtitles_en, link in services:
                if not Service.query.filter_by(title_en=title_en).first():
                    service = Service(
                        title_ru=title_ru,
                        title_tk=title_tk,
                        title_en=title_en,
                        subtitles_ru=subtitles_ru,
                        subtitles_tk=subtitles_tk,
                        subtitles_en=subtitles_en,
                        button_text_ru='Узнать больше',
                        button_text_tk='Köpräk bil',
                        button_text_en='Learn More',
                        button_link=link
                    )
                    db.session.add(service)

            if not Contact.query.first():
                contact = Contact(
                    phone="+99365 78 88 80 | +99312 34 45 56",
                    address_ru="Ул. Андалып, здание 'Сувар', 3-й этаж",
                    address_tk="Andalyp köçesi, 'Suwar' binasy, 3-nji gat",
                    address_en="Andalyp st. 'Suvar' building, 3rd floor",
                    email="tagmatelsalam@gmail.com",
                    social_media="@tagma.biz, @Tagma Projects"
                )
                db.session.add(contact)

            if not About.query.first():
                about = About(
                    title_ru="О нас",
                    title_tk="Biz barada",
                    title_en="About Us",
                    subtitle_ru="Tagma — динамичная ИТ-компания из Ашхабада, Туркменистан...",
                    subtitle_tk="Tagma — Türkmenistanyň Aşgabat şäherindäki dinamiki IT kompaniýasy...",
                    subtitle_en="Tagma is a dynamic IT company based in Ashgabat, Turkmenistan...",
                    description1_ru="В Tagma мы сочетаем передовые технологии с творческим опытом...",
                    description1_tk="Tagma-da biz öňdebaryjy tehnologiýalary döredijilik tejribesi bilen birleşdirýäris...",
                    description1_en="At Tagma, we combine cutting-edge technology with creative expertise...",
                    description2_ru="Основанная в 2015 году, мы стали надёжным партнёром...",
                    description2_tk="2015-nji ýylda esaslandyrylan, biz ynamdar hyzmatdaş bolduk...",
                    description2_en="Founded in 2015, we’ve grown into a trusted partner...",
                    image_url="/static/images/about_office.jpg"
                )
                db.session.add(about)

            db.session.commit()

        except OperationalError as e:
            print(f"Skipping seeding due to schema mismatch: {e}")
            db.session.rollback()

    return app