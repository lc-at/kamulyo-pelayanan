from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from app.models import BalasanTiket, Tiket, User, db

from app.messaging import KamulyoTiketUpdatedMessage, KamulyoTiketClosedMessage

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
        flash('Anda telah keluar', 'success')
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
    tiket_counts_data = {
        'baru': Tiket.get_tiket_baru_count(),
        'terbuka': Tiket.get_tiket_terbuka_count(),
        'selesai': Tiket.get_tiket_selesai_count(),
    }
    return render_template('admin/dashboard.html', tiket_counts_data=tiket_counts_data)


@bp.route('/tiket-terbuka')
def tiket_terbuka():
    tikets = Tiket.query.filter_by(selesai=False).all()
    return render_template('admin/tabel_tiket.html', title='Tiket Terbuka', tikets=tikets)


@bp.route('/tiket-selesai')
def tiket_selesai():
    tikets = Tiket.query.filter_by(selesai=True).all()
    return render_template('admin/tabel_tiket.html', title='Tiket Selesai', tikets=tikets)


@bp.route('/tiket/<tiket_id>')
def tiket_detail(tiket_id):
    tiket = Tiket.query.filter_by(id=tiket_id).first_or_404()

    return render_template('admin/tiket_detail.html', tiket=tiket)


@bp.route('/tiket/<tiket_id>/tambahBalasan', methods=['POST'])
def tiket_tambah_balasan(tiket_id):
    tiket = Tiket.query.filter_by(id=tiket_id, selesai=False).first_or_404()

    isi_balasan = request.form.get('isiBalasan')
    if not isi_balasan:
        abort(400)

    balasan = BalasanTiket(tiket.id, isi_balasan)
    db.session.add(balasan)
    db.session.commit()

    KamulyoTiketUpdatedMessage(tiket).send()

    flash('Balasan berhasil ditambahkan', 'success')
    return redirect(url_for('admin.tiket_detail', tiket_id=tiket_id))


@bp.route('/tiket/<tiket_id>/tandaiSelesai')
def tiket_tandai_selesai(tiket_id):
    tiket = Tiket.query.filter_by(id=tiket_id, selesai=False).first_or_404()
    tiket.selesai = 1

    db.session.commit()

    KamulyoTiketClosedMessage(tiket).send()

    flash('Tiket berhasil ditandai selesai', 'success')
    return redirect(url_for('admin.tiket_detail', tiket_id=tiket_id))
