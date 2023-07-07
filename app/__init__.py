from flask import Flask
from .models import db, hashids


def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env('FLASK')
    db.init_app(app)
    hashids.init_app(app)

    from .views import bp as views_bp
    from .admin import bp as admin_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
