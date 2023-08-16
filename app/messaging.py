from app.extensions import zenziva
from app.extensions.flask_zenziva import ZenzivaAPIError


class KamulyoMessage:
    def set_message(self, message):
        self._message = message

    def build(self) -> str:
        return self._message

    def send(self, phone_number):
        try:
            zenziva.send_whatsapp_message(phone_number, self.build())
        except ZenzivaAPIError:
            return False
        return True


class KamulyoOTPMessage(KamulyoMessage):
    def __init__(self, otp):
        self.set_message('Your OTP is ' + otp)


class KamulyoTicketCreatedMessage(KamulyoMessage):
    def __init__(self, ticket):
        self.set_message('Your ticket ' + ticket + ' has been created')


class KamulyoTicketUpdatedMessage(KamulyoMessage):
    def __init__(self, ticket):
        self.set_message('Your ticket ' + ticket + ' has been updated')


class KamulyoTicketClosedMessage(KamulyoMessage):
    def __init__(self, ticket):
        self.set_message('Your ticket ' + ticket + ' has been closed')
