from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_babel import _
from app.models.banner import Banner
from app.models.project import Project, Category
from app.models.blog import Blog
from app.models.client import Client
from app.models.service import Service
from app.models.review import Review
from app.models.user import User
from app.models.contact import Contact
from app.models.about import About

main_bp = Blueprint('main', __name__)

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
        'data': [banner.to_dict() for banner in banners()]
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
    categories = Project.query.all()
    return jsonify({
        'categories': 'success',
        'data': [category.to_dict() for category in categories]
    })

@main_bp.route('/api/services')
def get_services():
    services = Service.query.all()
    return jsonify({
        'status': 'success',
        'data': [service.to_dict() for service in services]
    })

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

@main_bp.route('/project/<slug>')
def project_detail(slug):
    project = Project.query.filter_by(button_link=f'/project/{slug}').first_or_404()
    return render_template('project.html', project=project)

@main_bp.route('/about')
def about():
    about = About.query.first()
    if not about:
        flash(_('No about information found'))
        return redirect(url_for('main.index'))
    return render_template('about.html', about=about, title=_('About Us'))