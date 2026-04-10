from flask import Flask, redirect, url_for, request, has_request_context, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.base import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from flask_cors import CORS
from flask_babel import Babel, _
from flask_ckeditor import CKEditor, CKEditorField
from markupsafe import Markup
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

    @expose('/')
    def index(self):
        # Import models here to avoid circular imports
        from app.models.banner import Banner
        from app.models.project import Project
        from app.models.blog import Blog
        from app.models.category import Category
        from app.models.client import Client
        from app.models.service import Service
        from app.models.partner import Partner
        from app.models.contact_request import ContactRequest

        try:
            counts = {
                'banners':    Banner.query.count(),
                'projects':   Project.query.count(),
                'blogs':      Blog.query.count(),
                'categories': Category.query.count(),
                'clients':    Client.query.count(),
                'services':   Service.query.count(),
                'partners':   Partner.query.count(),
                'requests':   ContactRequest.query.count(),
            }
            recent = ContactRequest.query.order_by(ContactRequest.id.desc()).limit(8).all()
        except Exception:
            counts = {k: 0 for k in ('banners','projects','blogs','categories','clients','services','partners','requests')}
            recent = []

        return self.render('admin/index.html',
                           admin_counts=counts,
                           recent_requests=recent)

class ModelAdminView(ModelView):
    extra_js = []  # CKEditor served locally via CKEDITOR_SERVE_LOCAL
    page_size = 25
    can_set_page_size = True

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def _list_thumbnail(self, context, model, name):
        url = getattr(model, name, None)
        if url:
            return Markup(f'<img src="{url}" style="max-height:50px;max-width:80px;object-fit:cover;border-radius:4px;">')
        return ''

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
        'id', 'title_ru', 'title_en', 'image_url', 'logo_url', 'button_link', 'created_at'
    )
    column_searchable_list = ('title_ru', 'title_en', 'button_link')
    column_sortable_list = ('id', 'title_ru', 'title_en', 'created_at')
    column_formatters = {
        'image_url': lambda v, c, m, n: v._list_thumbnail(c, m, 'image_url'),
        'logo_url':  lambda v, c, m, n: v._list_thumbnail(c, m, 'logo_url'),
    }
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

class ColorPickerWidget:
    """Renders an HTML5 color input with a live hex-value label."""
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs['type'] = 'color'
        kwargs['class'] = kwargs.get('class', '') + ' form-control form-control-color'
        kwargs['style'] = 'width:60px;height:38px;padding:2px;cursor:pointer;display:inline-block;vertical-align:middle;'
        value = field._value() or '#ffffff'
        kwargs['value'] = value
        html = (
            f'<input {html_params(name=field.name, **kwargs)}>'
            f'<span id="{field.id}_hex" style="margin-left:8px;font-family:monospace;vertical-align:middle;">'
            f'{value}</span>'
            f'<script>'
            f'(function(){{'
            f'  var inp=document.getElementById("{field.id}");'
            f'  var lbl=document.getElementById("{field.id}_hex");'
            f'  if(inp&&lbl){{'
            f'    inp.addEventListener("input",function(){{lbl.textContent=inp.value;}});'
            f'  }}'
            f'}})();'
            f'</script>'
        )
        return Markup(html)


class ColorField(StringField):
    widget = ColorPickerWidget()

    def _value(self):
        return self.data or '#ffffff'

class CategoryAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_en', 'slug', 'bg_color', 'created_at')
    column_searchable_list = ('title_ru', 'title_en', 'slug')
    column_sortable_list = ('id', 'title_ru', 'title_en', 'created_at')
    form_columns = ('title_ru', 'title_en', 'slug', 'link', 'bg_color', 'description_ru', 'description_en')
    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField,
        'bg_color': ColorField
    }

from wtforms.fields import SelectField
from wtforms.widgets import Select
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField as BaseQuerySelectMultipleField

class CompatibleQuerySelectField(QuerySelectField):
    def iter_choices(self):
        for choice in super().iter_choices():
            # WTForms 3.x expects 4-element tuples; pad older 3-element tuples
            if len(choice) == 3:
                yield choice + ({},)
            else:
                yield choice

class CompatibleQuerySelectMultipleField(BaseQuerySelectMultipleField):
    def iter_choices(self):
        for choice in super().iter_choices():
            # WTForms 3.x expects 4-element tuples; pad older 3-element tuples
            if len(choice) == 3:
                yield choice + ({},)
            else:
                yield choice

class PlainSelectField(SelectField):
    widget = Select()

    def iter_choices(self):
        for choice in super().iter_choices():
            # WTForms 3.x expects (value, label, selected, render_kw)
            if len(choice) == 3:
                yield choice + ({},)
            else:
                yield choice
from wtforms import TextAreaField
from wtforms.widgets import html_params
from app.models.project import Project
from app.utils.image_preview import MultipleImagePreviewField

class ProjectAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'main_image', 'type', 'bg_color', 'created_at'
    )
    column_searchable_list = ('title_ru', 'title_en', 'description_ru', 'description_en')
    column_sortable_list = ('id', 'title_ru', 'title_en', 'type', 'created_at')
    column_filters = ['type', 'created_at', 'categories.title_ru']
    column_formatters = {
        'main_image': lambda v, c, m, n: v._list_thumbnail(c, m, 'main_image'),
    }
    form_columns = (
        'title_ru', 'title_en', 'description_ru', 'description_en',
        'main_image_file', 'content_ru', 'content_en',
        'tags_ru_input', 'tags_en_input', 'bg_color', 'type', 'categories',
        'images_files', 'existing_images_preview'
    )

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
        'tags_ru_input': TextAreaField('Теги RU (через запятую)', description='Например: Брендинг, Дизайн'),
        'tags_en_input': TextAreaField('Теги EN (через запятую)', description='Например: Branding, Design'),
    }

    def on_form_prefill(self, form, id):
        project = self.model.query.get(id)
        if not project:
            return

        # Удаление изображения через query-параметр
        remove_image_url = request.args.get('remove_image')
        if remove_image_url and project.images and remove_image_url in project.images:
            project.images.remove(remove_image_url)
            try:
                abs_path = os.path.join(current_app.root_path, remove_image_url.lstrip('/'))
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            except Exception as e:
                current_app.logger.warning(f"Не удалось удалить файл: {e}")
            db.session.commit()

        # Обновлённый список изображений
        form.existing_images_preview.existing_images = project.images or []

        # Подставить теги в текстовые поля
        if project.tags_ru and isinstance(project.tags_ru, list):
            form.tags_ru_input.data = ', '.join(project.tags_ru)
        if project.tags_en and isinstance(project.tags_en, list):
            form.tags_en_input.data = ', '.join(project.tags_en)

    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField,
        'deliverables_ru': CKEditorField,
        'deliverables_en': CKEditorField,
        'type': PlainSelectField,
        'categories': CompatibleQuerySelectMultipleField,
        'bg_color': ColorField,
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
            filenames = list(model.images or [])
            for img in form.images_files.data:
                if img and hasattr(img, 'filename') and img.filename:
                    filename = secure_filename(img.filename)
                    file_path = os.path.join(upload_folder, filename)
                    current_app.logger.info(f"Сохранение дополнительного изображения в: {file_path}")
                    img.save(file_path)
                    filenames.append(f'/Uploads/{filename}')
            model.images = filenames

        if form.tags_ru_input.data:
            model.tags_ru = [t.strip() for t in form.tags_ru_input.data.split(',') if t.strip()]
        else:
            model.tags_ru = []

        if form.tags_en_input.data:
            model.tags_en = [t.strip() for t in form.tags_en_input.data.split(',') if t.strip()]
        else:
            model.tags_en = []

# Blog Admin
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField
from app.models.blog import Blog
from app.utils.file_upload import FileUploadField, MultipleFileUploadField
from werkzeug.utils import secure_filename
import os

class BlogAdminView(ModelAdminView):
    column_list = (
        'id', 'title_ru', 'title_en', 'image_url', 'date', 'created_at'
    )
    column_searchable_list = ('title_ru', 'title_en', 'description_ru', 'description_en')
    column_sortable_list = ('id', 'title_ru', 'title_en', 'date', 'created_at')
    column_formatters = {
        'image_url': lambda v, c, m, n: v._list_thumbnail(c, m, 'image_url'),
    }

    form_columns = (
        'title_ru', 'title_en', 'description_ru', 'description_en',
        'image_file', 'additional_images_files', 'date', 'read_time', 'link', 'tags_input'
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
        ),
        'tags_input': TextAreaField('Теги (через запятую)', description='Например: Branding, Design, Logo'),
    }

    form_overrides = {
        'description_ru': CKEditorField,
        'description_en': CKEditorField
    }

    def on_form_prefill(self, form, id):
        blog = self.model.query.get(id)
        if blog and blog.tags:
            form.tags_input.data = ', '.join(blog.tags)

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

        if form.tags_input.data:
            model.tags = [t.strip() for t in form.tags_input.data.split(',') if t.strip()]
        else:
            model.tags = []


# Client Admin
from app.models.client import Client
class ClientAdminView(ModelAdminView):
    column_list = ('id', 'logo_url', 'default_logo', 'created_at')
    column_sortable_list = ('id', 'created_at')
    column_formatters = {
        'logo_url':    lambda v, c, m, n: v._list_thumbnail(c, m, 'logo_url'),
        'default_logo': lambda v, c, m, n: v._list_thumbnail(c, m, 'default_logo'),
    }
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
    column_searchable_list = ('title_ru', 'title_en')
    column_sortable_list = ('id', 'title_ru', 'title_en')
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
        'about', 'title_ru', 'title_en', 'description_ru', 'description_en',
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
        'deliverables_en': CKEditorField,
        'color': ColorField,
        # WTForms 3.x compat: use patched select fields for relationships
        'about': CompatibleQuerySelectField,
        'categories': CompatibleQuerySelectMultipleField,
    }
    form_args = {
        'about': {
            'query_factory': lambda: About.query.all(),
            'get_label': 'title_ru',
            'allow_blank': True,
        },
        'categories': {
            'query_factory': lambda: Category.query.order_by(Category.title_ru),
            'get_label': 'title_ru',
            'allow_blank': True,
        },
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
from app.models.project import Project
from app.models.blog import Blog
class ServiceAdminView(ModelAdminView):
    column_list = ('id', 'category', 'created_at')
    column_sortable_list = ('id', 'created_at')
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
            'query_factory': lambda: Project.query.order_by(Project.title_ru),
            'get_label': 'title_ru',
            'allow_blank': True
        },
        'blogs': {
            'query_factory': lambda: Blog.query.order_by(Blog.title_ru),
            'get_label': 'title_ru',
            'allow_blank': True
        }
    })

    def on_model_change(self, form, model, is_created):
        if form.category.data:
            model.category = form.category.data


# Portfolio PDF Admin
from app.models.portfolio_pdf import PortfolioPDF
class PortfolioPDFAdminView(ModelAdminView):
    column_list = ('id', 'pdf_file')
    column_sortable_list = ('id',)
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
    column_searchable_list = ('username',)
    column_sortable_list = ('id', 'username', 'is_admin', 'created_at')
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
    column_list = ('id', 'phone', 'email', 'address_ru', 'created_at')
    column_searchable_list = ('phone', 'email')
    column_sortable_list = ('id', 'created_at')
    form_columns = ('phone', 'address_ru', 'address_tk', 'address_en', 'email', 'social_media')

from app.models.partner import Partner
class PartnerAdminView(ModelAdminView):
    column_list = ('id', 'name_ru', 'name_en', 'logo_url', 'created_at')
    column_searchable_list = ('name_ru', 'name_en')
    column_sortable_list = ('id', 'name_ru', 'name_en', 'created_at')
    column_formatters = {
        'logo_url': lambda v, c, m, n: v._list_thumbnail(c, m, 'logo_url'),
    }
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
from app.models.contact_request import ContactRequest

class ContactRequestAdmin(ModelAdminView):
    can_create = False
    can_edit = False
    can_delete = True

    column_list = ('id', 'full_name', 'email', 'phone', 'subject', 'meeting_date', 'terms_accepted')
    column_searchable_list = ('full_name', 'email', 'phone', 'message')
    column_sortable_list = ('id', 'full_name', 'email', 'meeting_date')
    column_filters = ('meeting_date', 'terms_accepted')

from app.models.review import Review
class ReviewAdminView(ModelAdminView):
    column_list = ('id', 'author_ru', 'author_en', 'content_ru', 'project_id', 'created_at')
    column_searchable_list = ('author_ru', 'author_en', 'content_ru', 'content_en')
    column_sortable_list = ('id', 'created_at')
    form_columns = ('content_ru', 'content_tk', 'content_en', 'author_ru', 'author_tk', 'author_en', 'project')
    # WTForms 3.x compat: patch QuerySelectField for the project FK relationship
    form_overrides = {
        'project': CompatibleQuerySelectField,
    }
    form_args = {
        'project': {
            'query_factory': lambda: Project.query.order_by(Project.title_ru),
            'get_label': 'title_ru',
            'allow_blank': True,
        }
    }

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
    # CKEditor — serve from flask-ckeditor bundled files (offline, no CDN)
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_PKG_TYPE'] = 'standard'
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

    admin = Admin(app, index_view=MyAdminIndexView(), template_mode='bootstrap4', name='Tagma Admin', base_template='admin/my_master.html')

    # --- Контент ---
    admin.add_view(BannerAdminView(Banner, db.session,       name=_('Banner'),        category=_('Content')))
    admin.add_view(ProjectAdminView(Project, db.session,     name=_('Project'),       category=_('Content')))
    admin.add_view(BlogAdminView(Blog, db.session,           name=_('Blog'),          category=_('Content')))
    admin.add_view(ServiceAdminView(Service, db.session,     name=_('Service'),       category=_('Content')))
    # --- Каталог ---
    admin.add_view(CategoryAdminView(Category, db.session,  name=_('Category'),      category=_('Catalog')))
    admin.add_view(ClientAdminView(Client, db.session,       name=_('Client'),        category=_('Catalog')))
    admin.add_view(PartnerAdminView(Partner, db.session,     name=_('Partner'),       category=_('Catalog')))
    # --- Настройки ---
    admin.add_view(AboutAdminView(About, db.session,         name=_('About'),         category=_('Settings')))
    admin.add_view(ContactAdminView(Contact, db.session,     name=_('Contact'),       category=_('Settings')))
    admin.add_view(PortfolioPDFAdminView(PortfolioPDF, db.session, name=_('Portfolio PDF'), category=_('Settings')))
    admin.add_view(UserAdminView(User, db.session,           name=_('User'),          category=_('Settings')))
    # --- Обращения ---
    admin.add_view(ContactRequestAdmin(ContactRequest, db.session, name=_('Contact Requests'), category=_('Requests')))
    admin.add_view(ReviewAdminView(Review, db.session, name=_('Reviews'), category=_('Content')))
    # --- Ссылки ---
    admin.add_link(MenuLink(name=_('Go to Website'), url='/'))
    admin.add_link(MenuLink(name=_('Logout'), url='/logout'))
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("База данных инициализирована успешно.")
        except OperationalError as e:
            app.logger.error(f"Ошибка при инициализации базы данных: {str(e)}")

    return app