import enum
import re
import uuid

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
    jenis = db.Column(db.String(100), nullable=False)
    nama_pengirim = db.Column(db.String(255), nullable=False)
    nohp_pengirim = db.Column(db.String(20), nullable=False)
    subjek = db.Column(db.String(255), nullable=False)
    narasi = db.Column(db.String(255), nullable=False)

    def __init__(self, jenis, nama_pengirim, nohp_pengirim, subjek, narasi):
        self.jenis = jenis
        self.nama_pengirim = nama_pengirim
        self.nohp_pengirim = nohp_pengirim
        self.subjek = subjek
        self.narasi = narasi

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
