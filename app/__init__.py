import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'admin.login'

# timezone utilities used by formatting filter
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # timezone-aware formatting filter
    def format_datetime(value, fmt='%d/%m/%Y %H:%M'):
        if value is None:
            return ''
        # treat naive timestamps as local (São Paulo) rather than UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo('America/Sao_Paulo'))
        return value.astimezone(ZoneInfo('America/Sao_Paulo')).strftime(fmt)

    app.jinja_env.filters['datetime'] = format_datetime

    from app import models
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


    # API blueprint for external access
    from app.api import bp as api_bp
    # ensure we only register once per app instance
    if 'api' not in app.blueprints:
        app.register_blueprint(api_bp, url_prefix='/api')

    # ensure initial administrator and regions exist
    with app.app_context():
        from app.models import User, Admin, Region
        # default credentials (can override via env for testing)
        default_phone = os.environ.get('DEFAULT_ADMIN_PHONE', '14 981364342')
        default_pass = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'jr34139251')
        default_name = os.environ.get('DEFAULT_ADMIN_NAME', 'ARNALDO MARTINS HIDALGO JUNIOR')
        # normalise into digits
        default_phone = ''.join(ch for ch in default_phone if ch.isdigit())

        # ensure there is at least one administrator with the default phone
        adm_user = User.query.filter_by(telefone=default_phone).first()
        if adm_user is None:
            # create new user+admin even if other admins exist
            u = User(telefone=default_phone, nome=default_name, cor='', region=None)
            db.session.add(u)
            db.session.commit()
            admin = Admin(user=u, is_original=True)
            admin.set_password(default_pass)
            db.session.add(admin)
            db.session.commit()
        else:
            # ensure the found user has an admin record
            if not adm_user.admin_record:
                admin = Admin(user=adm_user, is_original=True)
                admin.set_password(default_pass)
                db.session.add(admin)
                db.session.commit()
            # if there is an admin but the password may be wrong, do not overwrite blindly
            # but we could reset the hash if the account is marked original and the
            # password in DB doesn't verify.  Skip for now.

        # seed regions list
        defaults = ['branca','black','verde','roxa','amarela','laranja','azul celeste','azul marinho','vinho novo']
        for regname in defaults:
            if not Region.query.filter_by(nome=regname).first():
                db.session.add(Region(nome=regname))
        db.session.commit()

    return app
