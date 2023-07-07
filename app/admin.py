from flask import Blueprint, redirect, render_template, request, session, url_for

bp = Blueprint('admin', __name__)


@bp.before_request
def check_auth():
    if not session.get('logged_in') and request.endpoint != 'admin.login':
        return redirect(url_for('admin.login'))


@bp.route('/login')
def login():
    return render_template('admin/login.html')


@bp.route('/')
def index():
    return redirect(url_for('admin.login'))
