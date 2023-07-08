from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from app.models import User

bp = Blueprint('admin', __name__)


@bp.before_request
def check_auth():
    logged_in = session.get('user_id') is not None
    if request.endpoint == 'admin.login':
        if not logged_in:
            return
        return redirect(url_for('admin.dashboard'))

    if not session.get('user_id'):
        return redirect(url_for('admin.login'))

    user = User.query.get(session['user_id'])
    if not user:
        del session['user_id']
        abort(500)

    g.user = user


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not (username and password):
            abort(400)

        user_id = User.authenticate(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('admin.dashboard'))

        flash('Username atau password salah', 'danger')

    return render_template('admin/login.html')

@bp.route('/logout')
def logout():
    if g.user:
        del session['user_id']
        flash('Anda telah logout', 'success')
    return redirect(url_for('admin.login'))


@bp.route('/')
def index():
    return redirect(url_for('admin.login'))

@bp.route('/ganti-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if not password or password != password2:
            abort(400)

        g.user.change_password(password)
        flash('Password berhasil diganti', 'success')
        return redirect(url_for('admin.logout'))

    return render_template('admin/change_password.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')
