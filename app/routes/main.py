from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session, send_from_directory, current_app, abort
from flask_login import login_user, logout_user, login_required
from flask_babel import _
from app.models.banner import Banner
from app.models.project import Project
from app.models.category import Category
from app.models.blog import Blog
from app.models.client import Client
from app.models.service import Service
from app.models.review import Review
from app.models.user import User
from app.models.contact import Contact
from app.models.about import About
from app.forms.contact_steps import Step1Form, Step2Form, Step3Form
from app.models.contact_request import ContactRequest
from app import db
from datetime import datetime
from app.models.partner import Partner
from app.models.portfolio_pdf import PortfolioPDF
import os
from flask_babel import get_locale

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root_redirect():
    return redirect('/admin')

@main_bp.route('/')
@main_bp.route('/index')
def index():
    banners = Banner.query.all()
    return jsonify({
        'status': 'success',
        'message': _('Welcome to the Landing Page API'),
        'banners': [banner.to_dict() for banner in banners]
    })

@main_bp.route('/api/banners')
def get_banners():
    banners = Banner.query.all()
    return jsonify({
        'status': 'success',
        'data': [banner.to_dict() for banner in banners]
    })

@main_bp.route('/api/clients')
def get_clients():
    clients = Client.query.all()
    return jsonify({
        'status': 'success',
        'data': [client.to_dict() for client in clients]
    })
@main_bp.route('/api/categories')
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'status': 'success',
        'data': [category.to_dict() for category in categories]
    })

@main_bp.route('/api/services', methods=['GET', 'POST'])
def services():
    if request.method == 'GET':
        services = Service.query.all()
        return jsonify({
            'status': 'success',
            'data': [service.to_dict() for service in services]
        })
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No input data'}), 400

        service_id = data.get('id')
        if service_id:
            service = Service.query.get(service_id)
            if not service:
                return jsonify({'status': 'error', 'message': 'Service not found'}), 404
        else:
            service = Service()

        locale = str(get_locale()) or 'en'
        content_field = f'content_{locale}'

        setattr(service, content_field, data.get('content', ''))
        service.category_id = data.get('category_id')

        # TODO: обработка связей projects и blogs если нужно

        db.session.add(service)
        db.session.commit()

        return jsonify({'status': 'success', 'data': service.to_dict()}), 201
@main_bp.route('/api/partners')
def get_partners():
    partners = Partner.query.all()
    return jsonify({'status': 'success', 'data': [p.to_dict() for p in partners]})

@main_bp.route('/api/portfolio')
def get_portfolio():
    pdfs = PortfolioPDF.query.all()
    return jsonify({'status': 'success', 'data': [p.to_dict() for p in pdfs]})
@main_bp.route('/Uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
@main_bp.route('/api/contact-request', methods=['POST'])
def submit_contact_request():
    data = request.get_json()

    required_fields = ['full_name', 'email', 'phone', 'message']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({'status': 'error', 'message': f"Missing fields: {', '.join(missing)}"}), 400

    contact = ContactRequest.from_dict(data)
    db.session.add(contact)
    db.session.commit()

    return jsonify({'status': 'success', 'data': contact.to_dict()}), 201

@main_bp.route('/api/reviews')
def get_reviews():
    reviews = Review.query.all()
    return jsonify({
        'status': 'success',
        'data': [review.to_dict() for review in reviews]
    })

@main_bp.route('/api/contact')
def get_contact():
    contact = Contact.query.first()
    if not contact:
        return jsonify({'status': 'error', 'message': _('No contact information found')}), 404
    return jsonify({
        'status': 'success',
        'data': contact.to_dict()
    })

@main_bp.route('/api/about')
def get_about():
    about = About.query.first()
    if not about:
        return jsonify({'status': 'error', 'message': _('No about information found')}), 404
    return jsonify({
        'status': 'success',
        'data': about.to_dict()
    })

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        flash(_('Invalid username or password'))
        return redirect(url_for('main.login'))
    return render_template('login.html', title=_('Login'))

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- API блогов ---

@main_bp.route('/blog/', methods=['GET'])
def blogs_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()

    query = Blog.query
    if search:
        query = query.filter(
            (Blog.title_ru.ilike(f'%{search}%')) |
            (Blog.title_en.ilike(f'%{search}%'))
        )
    pagination = query.order_by(Blog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    blogs = pagination.items

    return jsonify({
        'status': 'success',
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'data': [blog.to_dict() for blog in blogs]
    })

@main_bp.route('/blog/<int:id>', methods=['GET'])
def blog_detail(id):
    blog = Blog.query.get_or_404(id)
    return jsonify({'status': 'success', 'data': blog.to_dict()})

# --- API проектов и работ (объединены) ---
@main_bp.route('/api/projects', methods=['POST'])
def create_or_update_project():
    # Просто перенаправить на существующий обработчик для projects_works
    return create_or_update_project_work()

@main_bp.route('/api/projects', methods=['GET'])
def projects_works_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()

    query = Project.query
    pagination = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items

    return jsonify({
        'status': 'success',
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'data': [item.to_dict() for item in items]
    })
@main_bp.route('/api/projects/<int:id>', methods=['GET'])
def project_work_detail(id):
    item = Project.query.get_or_404(id)
    return jsonify({'status': 'success', 'data': item.to_dict()})
