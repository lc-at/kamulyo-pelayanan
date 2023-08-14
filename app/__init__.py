from flask import Flask
from .models import db, hashids
from .whatsapp_verification_api import zenziva


def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env('FLASK')
    db.init_app(app)
    hashids.init_app(app)
    zenziva.init_app(app)

    from .views import bp as views_bp
    from .admin import bp as admin_bp
    from .whatsapp_verification_api import bp as whatsapp_verification_api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(whatsapp_verification_api_bp,
                           url_prefix='/api/whatsapp_verification')

    return app
