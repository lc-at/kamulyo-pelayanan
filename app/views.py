from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models import Tiket, db, hashids


bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        jenis = request.form.get('jenis')
        nama = request.form.get('nama')
        nohp = request.form.get('nomorHp')
        subjek = request.form.get('subjek')
        narasi = request.form.get('narasi')

        if not (jenis and nama and nohp and subjek and narasi):
            flash('Data tidak lengkap!', 'danger')
        else:
            tiket = Tiket(jenis, nama, nohp, subjek, narasi)
            if not tiket.validate():
                flash('Data tidak valid!', 'danger')
            else:
                db.session.add(tiket)
                db.session.commit()
                return redirect(url_for('main.form_next', tiket_id=tiket.public_id))

    return render_template('index.html')


@bp.route('/next/<tiket_id>')
@hashids.decode_or_404('tiket_id', first=True)
def form_next(tiket_id):
    tiket = Tiket.query.filter_by(id=tiket_id).first_or_404()
    return render_template('form_next.html', tiket=tiket)


@bp.route('/tiket')
def cari_tiket():
    tiket_id = request.args.get('idTiket')
    next_url = request.args.get('next', '/')

    if not tiket_id:
        flash('ID tiket tidak boleh kosong!', 'danger')
        return redirect(next_url)

    tiket_id = hashids.decode(tiket_id.strip().upper())
    if not tiket_id:
        flash('ID tiket tidak valid!', 'danger')
        return redirect(next_url)

    tiket = Tiket.query.filter_by(id=tiket_id[0]).first()
    if not tiket:
        flash('Tiket tidak ditemukan!', 'danger')
        return redirect(next_url)

    return redirect(url_for('main.form_next', tiket_id=tiket.public_id))
