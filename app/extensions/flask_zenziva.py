import requests


class ZenzivaExtension:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        userkey = app.config.get('ZENZIVA_USERKEY')
        passkey = app.config.get('ZENZIVA_PASSKEY')
        if not userkey or not passkey:
            raise RuntimeError(
                'ZENZIVA_USERKEY and ZENZIVA_PASSKEY must be set.')

        self._userkey = userkey
        self._passkey = passkey

    def send_whatsapp_message(self, whatsapp_number, message):
        url = 'https://console.zenziva.net/wareguler/api/sendWA/'
        data = {
            'userkey': self._userkey,
            'passkey': self._passkey,
            'to': whatsapp_number,
            'message': message
        }
        response = requests.post(url, data=data)
        if response.status_code != 201:
            print(response.text)
            raise Exception('Failed to send message to ' +
                            whatsapp_number + ' with message ' + message)
        return True
