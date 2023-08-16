from textwrap import dedent

from app.extensions import zenziva
from app.extensions.flask_zenziva import ZenzivaAPIError
from app.models import Tiket


class KamulyoMessage:
    def set_message(self, message):
        self._message = message

    def build(self) -> str:
        message_format = f'KamulyoPelayanan: {self._message}'
        return message_format

    def send(self, phone_number):
        try:
            zenziva.send_whatsapp_message(phone_number, self.build())
        except ZenzivaAPIError:
            return False
        return True


class KamulyoOTPMessage(KamulyoMessage):
    def __init__(self, otp):
        self.set_message(f'Kode v\x00erifikasi Anda adalah {otp}')


class KamulyoTiketRelatedMessage(KamulyoMessage):
    def __init__(self, tiket: Tiket):
        self.tiket = tiket

    def set_message(self, message):
        super().set_message(dedent(f'''\
            Halo {self.tiket.nama_pengirim},
            Ada informasi terkait tiket Anda dengan ID *{self.tiket.public_id}* 
            dan judul *{self.tiket.subjek}*

            *{message}*

            Untuk detail lebih lengkap, kunjungi link berikut:
            pelayanan.kamulyo.id/tiket/{self.tiket.public_id}
            '''))

    def send(self):
        super().send(self.tiket.nohp_pengirim)


class KamulyoTiketCreatedMessage(KamulyoTiketRelatedMessage):
    def __init__(self, tiket: Tiket):
        message = f'Tiket Anda telah dibuat'
        self.tiket = tiket
        self.set_message(message)


class KamulyoTiketUpdatedMessage(KamulyoTiketRelatedMessage):
    def __init__(self, tiket):
        message = f'Tiket Anda telah diperbarui'
        self.tiket = tiket
        self.set_message(message)


class KamulyoTiketClosedMessage(KamulyoTiketRelatedMessage):
    def __init__(self, tiket):
        message = f'Tiket Anda telah ditutup'
        self.tiket = tiket
        self.set_message(message)
