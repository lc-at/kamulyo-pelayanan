from functools import wraps
from flask import abort
from hashids import Hashids


class HashidsExtension:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        salt = app.config.get('HASHIDS_SALT')
        if not salt:
            raise RuntimeError('Missing HASHIDS_SALT configuration')

        extra_kwargs = {}
        if app.config.get('HASHIDS_ALPHABET'):
            extra_kwargs['alphabet'] = app.config['HASHIDS_ALPHABET']
        if app.config.get('HASHIDS_MIN_LENGTH'):
            extra_kwargs['min_length'] = app.config['HASHIDS_MIN_LENGTH']

        self._hashids = Hashids(salt, **extra_kwargs)
        app.extensions['hashids'] = self

    def decode_or_404(self, arg_name, *, first=False):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if arg_name in kwargs:
                    decoded = self.decode(kwargs[arg_name])
                    if not decoded:
                        abort(404)
                    elif first:
                        kwargs[arg_name] = decoded[0]
                    else:
                        kwargs[arg_name] = decoded

                return func(*args, **kwargs)

            return wrapper

        return decorator

    def encode(self, *args):
        return self._hashids.encode(*args)

    def decode(self, *args):
        return self._hashids.decode(*args)
