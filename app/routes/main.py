from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
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
from app.forms.contact_steps import Step1Form, Step2Form, Step3Form
from app.models.contact_request import ContactRequest
from app import db
from datetime import datetime
from app.models.partner import Partner

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

@main_bp.route('/contact/step1', methods=['GET', 'POST'])
def contact_step1():
    form = Step1Form()
    if form.validate_on_submit():
        contact = ContactRequest(
            full_name=form.full_name.data,
            company_name=form.company_name.data,
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()
        session['contact_request_id'] = contact.id
        return redirect(url_for('main.contact_step2'))
    return render_template('contact/step1.html', form=form)

@main_bp.route('/contact/step2', methods=['GET', 'POST'])
def contact_step2():
    form = Step2Form()
    contact_id = session.get('contact_request_id')
    if not contact_id:
        return redirect(url_for('main.contact_step1'))
    contact = ContactRequest.query.get(contact_id)
    if form.validate_on_submit():
        contact.meeting_date = form.meeting_date.data
        contact.meeting_time = form.meeting_time.data
        contact.timezone = form.timezone.data
        db.session.commit()
        return redirect(url_for('main.contact_step3'))
    return render_template('contact/step2.html', form=form)

@main_bp.route('/contact/step3', methods=['GET', 'POST'])
def contact_step3():
    form = Step3Form()
    contact_id = session.get('contact_request_id')
    if not contact_id:
        return redirect(url_for('main.contact_step1'))
    contact = ContactRequest.query.get(contact_id)
    if form.validate_on_submit():
        contact.terms_accepted = form.terms_accepted.data
        db.session.commit()
        session.pop('contact_request_id', None)
        flash('Your request has been submitted!', 'success')
        return redirect(url_for('main.contact_step1'))
    return render_template('contact/step3.html', form=form)

@main_bp.route('/api/contact-request', methods=['POST'])
def api_contact_request():
    data = request.get_json()
    # Преобразуем строку в date
    meeting_date = data.get('meeting_date')
    if meeting_date:
        try:
            meeting_date = datetime.strptime(meeting_date, "%Y-%m-%d").date()
        except Exception:
            meeting_date = None

    contact = ContactRequest(
        full_name=data.get('full_name'),
        company_name=data.get('company_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        subject=data.get('subject'),
        message=data.get('message'),
        meeting_date=meeting_date,
        meeting_time=data.get('meeting_time'),
        timezone=data.get('timezone'),
        terms_accepted=data.get('terms_accepted', False)
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify({'status': 'success', 'id': contact.id}), 201

@main_bp.route('/api/partners')
def get_partners():
    partners = Partner.query.all()
    return jsonify({
        'status': 'success',
        'data': [
            {
                'name': p.name,
                'logo_url': p.logo_url,
                'description': p.description
            } for p in partners
        ]
    })

@main_bp.route('/blogs', methods=['GET'])
def blogs_list():
    search = request.args.get('search', '').strip()
    query = Blog.query
    if search:
        query = query.filter(
            (Blog.title_ru.ilike(f'%{search}%')) |
            (Blog.title_en.ilike(f'%{search}%')) |
            (Blog.title_tk.ilike(f'%{search}%'))
        )
    blogs = query.order_by(Blog.created_at.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [blog.to_dict() for blog in blogs]
    })