import secrets

from flask import Blueprint, abort, request

from app.extensions import redis_client
from app.messaging import KamulyoOTPMessage

bp = Blueprint('whatsapp_verification_api', __name__)


class OTPSession:
    def __init__(self, phone_number,
                 redis_client=redis_client,
                 redis_key_prefix='rotp'):

        self._redis_client = redis_client
        self._otp_redis_key = f'{redis_key_prefix}:otp:{phone_number}'
        self._auth_token_redis_key = f'{redis_key_prefix}:auth_token:{phone_number}'

    def _generate_random_otp(self):
        return str(secrets.randbelow(1_000_000)).zfill(6)

    def _set_random_expiring_otp(self):
        random_otp = self._generate_random_otp()
        self._redis_client.set(self._otp_redis_key, random_otp, ex=120)

    def get_otp(self):
        otp = self._redis_client.get(self._otp_redis_key)
        if otp:
            return otp.decode('utf-8')

    def revoke_otp(self):
        self._redis_client.delete(self._otp_redis_key)

    def is_expired(self):
        return not self.get_otp()

    def get_and_set_otp_if_none(self):
        if not self.get_otp():
            self._set_random_expiring_otp()
        return self.get_otp()

    def verify_otp(self, input_otp):
        return self.get_otp() == input_otp

    def generate_auth_token(self):
        auth_token = secrets.token_urlsafe()
        self._redis_client.set(self._auth_token_redis_key, auth_token, ex=3600)
        return auth_token

    def _get_auth_token(self):
        auth_token = self._redis_client.get(
            self._auth_token_redis_key)
        if auth_token:
            return auth_token.decode('utf-8')

    def verify_auth_token(self, auth_token):
        if not auth_token:
            return False
        return self._get_auth_token() == auth_token

    def revoke_auth_token(self):
        self._redis_client.delete(self._auth_token_redis_key)


@bp.route('/otp', methods=['POST'])
def send_otp():
    nomor_whatsapp = request.form.get('nomorWhatsapp')
    if not nomor_whatsapp:
        abort(400)

    otp_session = OTPSession(nomor_whatsapp)

    if not otp_session.is_expired():
        return {'message': 'OTP masih berlaku'}, 400

    otp_code = otp_session.get_and_set_otp_if_none()

    message = KamulyoOTPMessage(otp_code)
    if not message.send(nomor_whatsapp):
        otp_session.revoke_otp()
        return {'message': 'OTP gagal dikirim'}, 500

    return {'message': 'OTP berhasil dikirim'}


@bp.route('/auth_token')
def get_auth_token():
    nomor_whatsapp = request.args.get('nomorWhatsapp')
    input_otp = request.args.get('otp')
    if not nomor_whatsapp or not input_otp:
        abort(400)

    otp_session = OTPSession(nomor_whatsapp)
    if otp_session.verify_otp(input_otp):
        return {'message': 'Success', 'auth_token': otp_session.generate_auth_token()}
    else:
        return {'message': 'Invalid OTP'}, 400
