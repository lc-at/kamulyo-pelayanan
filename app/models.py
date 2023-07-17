import enum
import re

from typing import Union

from passlib.hash import pbkdf2_sha256
from flask_sqlalchemy import SQLAlchemy
from app.extensions.flask_hashids import HashidsExtension

db = SQLAlchemy()
hashids = HashidsExtension()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(87), nullable=False)

    def __init__(self, username, plain_password):
        self.username = username
        self.password = pbkdf2_sha256.hash(plain_password)

    def change_password(self, new_password):
        self.password = pbkdf2_sha256.hash(new_password)
        db.session.commit()

    @classmethod
    def authenticate(cls, username, password) -> Union[int, None]:
        user: User = cls.query.filter_by(username=username).first()
        if not user and username == 'admin':
            user = User('admin', 'password')
            db.session.add(user)
            db.session.commit()
            return user.id

        if user and pbkdf2_sha256.verify(password, user.password):
            return user.id


class JenisTiket(str, enum.Enum):
    PENGADUAN = 'pengaduan'
    PENGAJUAN = 'pengajuan'


class Tiket(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_publik = db.Column(db.Boolean, nullable=False, default=False)
    jenis = db.Column(db.String(100), nullable=False)
    nama_pengirim = db.Column(db.String(255), nullable=False)
    nohp_pengirim = db.Column(db.String(20), nullable=False)
    subjek = db.Column(db.String(255), nullable=False)
    narasi = db.Column(db.String(255), nullable=False)
    selesai = db.Column(db.Boolean, nullable=False, default=False)
    tgl_dibuat = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now())
    balasans = db.relationship('BalasanTiket',
                               backref='tiket',
                               lazy=True)

    def __init__(self, jenis, nama_pengirim, nohp_pengirim, subjek, narasi, is_publik):
        self.jenis = jenis
        self.nama_pengirim = nama_pengirim
        self.nohp_pengirim = nohp_pengirim
        self.subjek = subjek
        self.narasi = narasi
        self.is_publik = is_publik

    @property
    def public_id(self):
        return hashids.encode(self.id)

    def validate(self) -> bool:
        try:
            JenisTiket(self.jenis)
        except ValueError:
            return False

        if not re.match(r'^08\d{5,13}$', self.nohp_pengirim):
            return False

        return True

    @staticmethod
    def clean_public_id(tiket_public_id: str):
        return re.sub(r'[^A-Z0-9]', '', tiket_public_id.upper())

    @classmethod
    def from_public_id(cls, tiket_public_id):
        tiket_public_id = cls.clean_public_id(tiket_public_id)
        public_tiket_id_decoded = hashids.decode(tiket_public_id)
        if not public_tiket_id_decoded:
            return None
        # tiket_id is the first
        return cls.query.get(public_tiket_id_decoded[0])


class BalasanTiket(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tiket_id = db.Column(db.Integer, db.ForeignKey('tiket.id'), nullable=False)
    isi = db.Column(db.Text, nullable=False)
    tgl_dibuat = db.Column(db.DateTime,
                           nullable=False,
                           server_default=db.func.now())

    def __init__(self, tiket_id, isi):
        self.tiket_id = tiket_id
        self.isi = isi
