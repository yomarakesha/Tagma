from flask import Flask, redirect, url_for, request, has_request_context
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Field, Select2Widget
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from flask_cors import CORS
from flask_babel import Babel, _, get_locale
from flask_ckeditor import CKEditor, CKEditorField
import os
from datetime import datetime
from sqlalchemy.exc import OperationalError
from werkzeug.utils import secure_filename
from app.utils.file_upload import FileUploadField, MultipleFileUploadField
from wtforms import TextAreaField
from wtforms.fields import SelectMultipleField, PasswordField
from wtforms import validators
from flask import current_app
import errno
import stat
import logging
import tempfile

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
ckeditor = CKEditor()

# Конфигурация загрузки файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Кастомное поле для Quill Editor
class QuillTextAreaField(TextAreaField):
    pass

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

    def _run_view(self, fn, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Ошибка в представлении: {str(e)}")
            raise

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

class BannerAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'image_url', 'button_text_ru', 'button_text_tk', 'button_text_en', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'subtitle_ru', 'subtitle_tk', 'subtitle_en', 'image_file', 'button_text_ru', 'button_text_tk', 'button_text_en', 'button_link')
    form_extra_fields = {
        'image_file': FileUploadField(_('Изображение баннера'), base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        current_app.logger.info(f"on_model_change вызван для модели {model.id if model.id else 'новой'}. Данные формы: {form.data}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)

        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить изображение в: {file_path}")
            try:
                form.image_file.data.save(file_path)
                current_app.logger.info(f"Изображение сохранено в {file_path}")
                model.image_url = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить изображение в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить изображение: {str(e)}")
        if not model.image_url and is_created:
            raise ValueError(_("Изображение баннера обязательно"))

class ProjectAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'background_image_url', 'button_text_ru', 'button_text_tk', 'button_text_en', 'pdf_file', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'description_ru', 'description_tk', 'description_en', 'background_image_file', 'pdf_file', 'button_text_ru', 'button_text_tk', 'button_text_en', 'button_link', 'deliverables_ru', 'deliverables_tk', 'deliverables_en', 'categories')
    form_extra_fields = {
        'background_image_file': FileUploadField(_('Фоновое изображение'), base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
        'pdf_file': FileUploadField(_('PDF-файл'), base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions={'pdf'}),
        'description_ru': CKEditorField(_('Описание (Русский)')),
        'description_tk': CKEditorField(_('Описание (Туркменский)')),
        'description_en': CKEditorField(_('Описание (Английский)')),
        'deliverables_ru': CKEditorField(_('Доставляемое (Русский)')),
        'deliverables_tk': CKEditorField(_('Доставляемое (Туркменский)')),
        'deliverables_en': CKEditorField(_('Доставляемое (Английский)')),
        'categories': SelectMultipleField(
            _('Категории'),
            coerce=int,
            widget=Select2Widget(multiple=True),
            validators=[validators.Optional()]
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
    column_filters = ['categories.name_en']

    def get_form(self):
        form = super().get_form()
        return form

    def create_form(self):
        form = super().create_form()
        from app.models.category import Category
        with current_app.app_context():
            categories = db.session.query(Category).all()
            choices = [(c.id, c.name_en) for c in categories if c.id and c.name_en]
            current_app.logger.info(f"Create form categories choices: {choices}")
            if not choices:
                current_app.logger.warning("Категории не найдены. Добавляем стандартные категории.")
                default_categories = [
                    ('Дизайн брендинга', 'Brending dizaýny', 'Branding Design'),
                    ('ИТ-консультации', 'IT maslahat berişlik', 'IT Consulting')
                ]
                for name_ru, name_tk, name_en in default_categories:
                    if not Category.query.filter_by(name_en=name_en).first():
                        cat = Category(name_ru=name_ru, name_tk=name_tk, name_en=name_en)
                        db.session.add(cat)
                db.session.commit()
                categories = db.session.query(Category).all()
                choices = [(c.id, c.name_en) for c in categories if c.id and c.name_en]
            form.categories.choices = choices
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        from app.models.category import Category
        with current_app.app_context():
            categories = db.session.query(Category).all()
            choices = [(c.id, c.name_en) for c in categories if c.id and c.name_en]
            current_app.logger.info(f"Edit form categories choices: {choices}")
            if not choices:
                current_app.logger.warning("Категории не найдены при редактировании. Добавляем стандартные категории.")
                default_categories = [
                    ('Дизайн брендинга', 'Brending dizaýny', 'Branding Design'),
                    ('ИТ-консультации', 'IT maslahat berişlik', 'IT Consulting')
                ]
                for name_ru, name_tk, name_en in default_categories:
                    if not Category.query.filter_by(name_en=name_en).first():
                        cat = Category(name_ru=name_ru, name_tk=name_tk, name_en=name_en)
                        db.session.add(cat)
                db.session.commit()
                categories = db.session.query(Category).all()
                choices = [(c.id, c.name_en) for c in categories if c.id and c.name_en]
            form.categories.choices = choices
            if obj:
                form.categories.data = [c.id for c in obj.categories] if obj.categories else []
                current_app.logger.info(f"Текущие категории для проекта {obj.id}: {form.categories.data}")
        return form

    def update_model(self, form, model):
        try:
            form_data = form.data
            current_app.logger.info(f"Данные формы: {form_data}")
            
            model.title_ru = form_data.get('title_ru', model.title_ru)
            model.title_tk = form_data.get('title_tk', model.title_tk)
            model.title_en = form_data.get('title_en', model.title_en)
            model.description_ru = form_data.get('description_ru', model.description_ru)
            model.description_tk = form_data.get('description_tk', model.description_tk)
            model.description_en = form_data.get('description_en', model.description_en)
            model.button_text_ru = form_data.get('button_text_ru', model.button_text_ru)
            model.button_text_tk = form_data.get('button_text_tk', model.button_text_tk)
            model.button_text_en = form_data.get('button_text_en', model.button_text_en)
            model.button_link = form_data.get('button_link', model.button_link)
            model.deliverables_ru = form_data.get('deliverables_ru', model.deliverables_ru)
            model.deliverables_tk = form_data.get('deliverables_tk', model.deliverables_tk)
            model.deliverables_en = form_data.get('deliverables_en', model.deliverables_en)

            from app.models.category import Category
            selected_category_ids = form_data.get('categories', [])
            if selected_category_ids and not isinstance(selected_category_ids, (list, tuple)):
                selected_category_ids = [selected_category_ids]
            selected_category_ids = [int(id) for id in selected_category_ids if id]
            current_app.logger.info(f"Выбранные ID категорий: {selected_category_ids}")
            
            model.categories.clear()
            if selected_category_ids:
                selected_categories = Category.query.filter(Category.id.in_(selected_category_ids)).all()
                for category in selected_categories:
                    model.categories.append(category)
                current_app.logger.info(f"Назначены категории модели: {[c.name_en for c in model.categories]}")
            else:
                model.categories = []
                current_app.logger.info("Категории не выбраны, очищены категории модели")

            self.on_model_change(form, model, False)
            db.session.commit()
            current_app.logger.info("Изменения успешно сохранены")
            return True
        except Exception as ex:
            current_app.logger.error(f"Не удалось обновить модель: {str(ex)}")
            db.session.rollback()
            if not self.handle_view_exception(ex):
                raise
            return False

    def on_model_change(self, form, model, is_created):
        current_app.logger.info(f"on_model_change вызван для модели {model.id if model.id else 'новой'}. Данные формы: {form.data}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)

        if form.background_image_file.data:
            filename = secure_filename(form.background_image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить фоновое изображение в: {file_path}")
            try:
                form.background_image_file.data.save(file_path)
                current_app.logger.info(f"Фоновое изображение сохранено в {file_path}")
                model.background_image_url = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить фоновое изображение в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить фоновое изображение: {str(e)}")

        if form.pdf_file.data:
            filename = secure_filename(form.pdf_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить PDF в: {file_path}")
            try:
                form.pdf_file.data.save(file_path)
                current_app.logger.info(f"PDF сохранён в {file_path}")
                model.pdf_file = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить PDF в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить PDF: {str(e)}")

class BlogAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'date', 'read_time', 'image_url', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'description_ru', 'description_tk', 'description_en', 'image_file', 'additional_images_files', 'date', 'read_time', 'link')
    form_extra_fields = {
        'image_file': FileUploadField(_('Основное изображение'), base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
        'additional_images_files': MultipleFileUploadField(_('Дополнительные изображения'), base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS),
        'description_ru': CKEditorField(_('Описание (Русский)')),
        'description_tk': CKEditorField(_('Описание (Туркменский)')),
        'description_en': CKEditorField(_('Описание (Английский)'))
    }
    form_widget_args = {
        'description_ru': {'class': 'quill-editor'},
        'description_tk': {'class': 'quill-editor'},
        'description_en': {'class': 'quill-editor'}
    }
    edit_template = 'admin/blog_edit.html'

    def on_model_change(self, form, model, is_created):
        current_app.logger.info(f"on_model_change вызван для модели {model.id if model.id else 'новой'}. Данные формы: {form.data}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)

        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить основное изображение в: {file_path}")
            try:
                form.image_file.data.save(file_path)
                current_app.logger.info(f"Основное изображение сохранено в {file_path}")
                model.image_url = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить основное изображение в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить основное изображение: {str(e)}")

        if form.additional_images_files.data:
            self._handle_additional_images(form.additional_images_files.data, model, upload_folder)

        if not model.image_url and is_created:
            raise ValueError(_("Основное изображение обязательно"))

    def _handle_additional_images(self, files, model, upload_folder):
        additional_images = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                current_app.logger.info(f"Попытка сохранить дополнительное изображение в: {file_path}")
                try:
                    file.save(file_path)
                    current_app.logger.info(f"Дополнительное изображение сохранено в {file_path}")
                    additional_images.append(f'/Uploads/{filename}')
                except Exception as e:
                    current_app.logger.error(f"Не удалось сохранить дополнительное изображение в {file_path}: {str(e)}")
                    raise ValueError(f"Не удалось сохранить дополнительное изображение: {str(e)}")
        model.additional_images = ','.join(additional_images) if additional_images else None

class ClientAdminView(ModelAdminView):
    column_list = ('id', 'logo_url', 'created_at')
    form_columns = ('logo_file',)
    form_extra_fields = {
        'logo_file': FileUploadField(_('Логотип клиента'), base_path=lambda: current_app.config['UPLOAD_FOLDER'], allowed_extensions=ALLOWED_EXTENSIONS)
    }

    def on_model_change(self, form, model, is_created):
        current_app.logger.info(f"on_model_change вызван для модели {model.id if model.id else 'новой'}. Данные формы: {form.data}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)

        if form.logo_file.data:
            filename = secure_filename(form.logo_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить логотип в: {file_path}")
            try:
                form.logo_file.data.save(file_path)
                current_app.logger.info(f"Логотип сохранён в {file_path}")
                model.logo_url = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить логотип в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить логотип: {str(e)}")
        if not model.logo_url and is_created:
            raise ValueError(_("Логотип клиента обязателен"))

class AboutAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'image_url', 'created_at')
    form_columns = (
        'title_ru', 'title_tk', 'title_en',
        'subtitle_ru', 'subtitle_tk', 'subtitle_en',
        'description1_ru', 'description1_tk', 'description1_en',
        'description2_ru', 'description2_tk', 'description2_en',
        'address', 'image_file', 'logo_file', 'image_file2'
    )
    form_extra_fields = {
        'image_file': FileUploadField(
            _('Изображение страницы'),
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        ),
        'logo_file': FileUploadField(
            _('Логотип'),
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        ),
        'image_file2': FileUploadField(
            _('Дополнительное изображение'),
            base_path=lambda: current_app.config['UPLOAD_FOLDER'],
            allowed_extensions=ALLOWED_EXTENSIONS
        ),
        'description1_ru': CKEditorField(_('Описание 1 (Русский)')),
        'description1_tk': CKEditorField(_('Описание 1 (Туркменский)')),
        'description1_en': CKEditorField(_('Описание 1 (Английский)')),
        'description2_ru': CKEditorField(_('Описание 2 (Русский)')),
        'description2_tk': CKEditorField(_('Описание 2 (Туркменский)')),
        'description2_en': CKEditorField(_('Описание 2 (Английский)')),
    }
    form_widget_args = {
        'description1_ru': {'class': 'quill-editor'},
        'description1_tk': {'class': 'quill-editor'},
        'description1_en': {'class': 'quill-editor'},
        'description2_ru': {'class': 'quill-editor'},
        'description2_tk': {'class': 'quill-editor'},
        'description2_en': {'class': 'quill-editor'},
    }

    def on_model_change(self, form, model, is_created):
        current_app.logger.info(f"on_model_change вызван для модели {model.id if model.id else 'новой'}. Данные формы: {form.data}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        self._ensure_upload_folder(upload_folder)

        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить изображение в: {file_path}")
            try:
                form.image_file.data.save(file_path)
                current_app.logger.info(f"Изображение сохранено в {file_path}")
                model.image_url = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить изображение в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить изображение: {str(e)}")

        if form.logo_file.data:
            filename = secure_filename(form.logo_file.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить логотип в: {file_path}")
            try:
                form.logo_file.data.save(file_path)
                current_app.logger.info(f"Логотип сохранён в {file_path}")
                model.logo_url = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить логотип в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить логотип: {str(e)}")

        if form.image_file2.data:
            filename = secure_filename(form.image_file2.data.filename)
            file_path = os.path.join(upload_folder, filename)
            current_app.logger.info(f"Попытка сохранить дополнительное изображение в: {file_path}")
            try:
                form.image_file2.data.save(file_path)
                current_app.logger.info(f"Дополнительное изображение сохранено в {file_path}")
                model.image_url2 = f'/Uploads/{filename}'
            except Exception as e:
                current_app.logger.error(f"Не удалось сохранить дополнительное изображение в {file_path}: {str(e)}")
                raise ValueError(f"Не удалось сохранить дополнительное изображение: {str(e)}")

        if not model.image_url and is_created:
            raise ValueError(_("Изображение страницы обязательно"))

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

class CategoryAdminView(ModelAdminView):
    column_list = ('id', 'name_ru', 'name_tk', 'name_en', 'created_at')
    form_columns = ('name_ru', 'name_tk', 'name_en')

class ServiceAdminView(ModelAdminView):
    column_list = ('id', 'title_ru', 'title_tk', 'title_en', 'button_text_ru', 'button_text_tk', 'button_text_en', 'created_at')
    form_columns = ('title_ru', 'title_tk', 'title_en', 'subtitles_ru', 'subtitles_tk', 'subtitles_en', 'button_text_ru', 'button_text_tk', 'button_text_en', 'button_link')
    form_extra_fields = {
        'subtitles_ru': CKEditorField(_('Описание (Русский)')),
        'subtitles_tk': CKEditorField(_('Описание (Туркменский)')),
        'subtitles_en': CKEditorField(_('Описание (Английский)')),
    }
    form_widget_args = {
        'subtitles_ru': {'class': 'quill-editor'},
        'subtitles_tk': {'class': 'quill-editor'},
        'subtitles_en': {'class': 'quill-editor'},
    }

class ReviewAdminView(ModelAdminView):
    column_list = ('id', 'content_ru', 'content_tk', 'content_en', 'author_ru', 'author_tk', 'author_en', 'project_id', 'created_at')
    form_columns = ('content_ru', 'content_tk', 'content_en', 'author_ru', 'author_tk', 'author_en', 'project')
    form_extra_fields = {
        'content_ru': CKEditorField(_('Отзыв (Русский)')),
        'content_tk': CKEditorField(_('Отзыв (Туркменский)')),
        'content_en': CKEditorField(_('Отзыв (Английский)')),
        'project': Select2Field(
            _('Проект'),
            coerce=int,
            widget=Select2Widget(),
            validators=[validators.DataRequired()]
        )
    }
    form_widget_args = {
        'content_ru': {'class': 'quill-editor'},
        'content_tk': {'class': 'quill-editor'},
        'content_en': {'class': 'quill-editor'},
    }

    def get_form(self):
        return super().get_form()

    def create_form(self):
        form = super().create_form()
        from app.models.project import Project
        with current_app.app_context():
            try:
                projects = db.session.query(Project).all() or []
                choices = [(str(p.id), p.title_en) for p in projects if p.id and p.title_en]
                if not choices:
                    choices = [('0', 'Нет доступных проектов')]
                if hasattr(form, 'project'):
                    form.project.choices = choices
                    current_app.logger.info(f"Create form project choices: {choices}")
                else:
                    current_app.logger.error("Поле 'project' не найдено в форме при создании")
            except Exception as e:
                current_app.logger.error(f"Ошибка при установке choices для project в create_form: {str(e)}")
                form.project.choices = [('0', 'Нет доступных проектов')]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        from app.models.project import Project
        with current_app.app_context():
            try:
                projects = db.session.query(Project).all() or []
                choices = [(str(p.id), p.title_en) for p in projects if p.id and p.title_en]
                if not choices:
                    choices = [('0', 'Нет доступных проектов')]
                if hasattr(form, 'project'):
                    form.project.choices = choices
                    if obj and obj.project_id:
                        form.project.data = str(obj.project_id)
                    current_app.logger.info(f"Edit form project choices: {choices}")
                else:
                    current_app.logger.error("Поле 'project' не найдено в форме при редактировании")
            except Exception as e:
                current_app.logger.error(f"Ошибка при установке choices для project в edit_form: {str(e)}")
                form.project.choices = [('0', 'Нет доступных проектов')]
        return form

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

    admin = Admin(app, name='Панель администратора', template_mode='bootstrap3', index_view=MyAdminIndexView())
    from app.models.banner import Banner
    from app.models.project import Project
    from app.models.category import Category
    from app.models.blog import Blog
    from app.models.client import Client
    from app.models.service import Service
    from app.models.review import Review
    from app.models.contact import Contact
    from app.models.about import About
    from app.models.contact_request import ContactRequest
    from app.models.partner import Partner

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
    admin.add_view(ModelAdminView(ContactRequest, db.session, name="Contact Requests"))
    admin.add_view(ModelAdminView(Partner, db.session, name="Partners"))

    with app.app_context():
        admin.add_link(MenuLink(name=_('Выход'), url='/logout'))

    from app.api.resources import init_api
    init_api(app)

    with app.app_context():
        try:
            # Создаём все таблицы перед инициализацией данных
            db.create_all()
            app.logger.info("Все таблицы успешно созданы")

            # Инициализация данных
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
                    image_url='/Uploads/banner.jpg',
                    button_text_ru='Посмотрите, что мы можем сделать',
                    button_text_tk='Biziň näme edip biljekdigimizi görüň',
                    button_text_en='See what we can do',
                    button_link='/services'
                )
                db.session.add(banner)

            if not Category.query.first():
                categories = [
                    ('Дизайн брендинга', 'Brending dizaýny', 'Branding Design'),
                    ('ИТ-консультации', 'IT maslahat berişlik', 'IT Consulting'),
                    ('Решения для инженерных заводов', 'Zawod inženerçilik çözgütleri', 'Factory Engineering Solutions'),
                    ('Промышленные продукты', 'Senagat önümleri', 'Industrial IT')
                ]
                for name_ru, name_tk, name_en in categories:
                    if not Category.query.filter_by(name_en=name_en).first():
                        db.session.add(Category(name_ru=name_ru, name_tk=name_tk, name_en=name_en))

            if not Project.query.first():
                branding = Category.query.filter_by(name_en='Branding Design').first()
                project = Project(
                    title_ru='Лампа Qwatt LED',
                    title_tk='Qwatt LED-',
                    title_en='Qwatt LED Bulb',
                    description_ru='Брендинг Tagma сияет в идентичности Qwatt — яркий, смелый и вечный, как её светодиоды.',
                    description_tk='Tagmanyň brendingi Qwatt-yň şahsyýetinde ýalpyldawuk — ýagty, batyr we öçmejek, ýaly LED-ler.',
                    description_en="Tagma's Branding Shines Through In Qwatt's identity-Bright, Bold, And Timeless, Just Like its LEDs.",
                    background_image_url='/Uploads/qwatt_lamp.jpg',
                    button_text_ru='Посмотреть проект',
                    button_text_tk='Tasar görmek',
                    button_text_en='View project',
                    button_link='/project/qwatt',
                    pdf_file=None
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
                    background_image_url='/Uploads/digital_transformation.jpg',
                    button_text_ru='Посмотреть проект',
                    button_text_tk='Tasar görmek',
                    button_text_en='View project',
                    button_link='/project/digital',
                    deliverables_ru=deliverables,
                    deliverables_tk=deliverables,
                    deliverables_en=deliverables,
                    pdf_file=None
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
                        project_id=project.id
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
                        read_time='3 мин чтения',
                        image_url=f'/Uploads/masterplan{i}.jpg',
                        link='/',
                        description_ru='Мы рады объявить о запуске Wallis Creek...',
                        description_tk='Wallis Creek-iň açylyşyndan buýsanýarys...',
                        description_en="We're excited to announce the launch of Wallis Creek...",
                        additional_images=None
                    )
                    db.session.add(blog)

            if not Client.query.first():
                client = Client(logo_url='/Uploads/hues.png')
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
                    image_url="/Uploads/about_office.jpg",
                    address="Ashgabat, Turkmenistan",
                    logo_url="/Uploads/tagma_logo.png",
                    image_url2="/Uploads/about_team.jpg"
                )
                db.session.add(about)

            db.session.commit()
            current_app.logger.info("Инициализация данных успешно завершена")

        except OperationalError as e:
            current_app.logger.error(f"Пропуск инициализации данных из-за несоответствия схемы: {str(e)}")
            db.session.rollback()

    return app

if __name__ == '__main__':
    app = create_app()