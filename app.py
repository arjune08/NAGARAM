import os
from flask import Flask, jsonify, render_template, send_from_directory
from flask_login import LoginManager, current_user
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from config import Config
from models import db, User
import farmer_models


class RootTemplateLoader(FileSystemLoader):
    def get_source(self, environment, template):
        try:
            return super().get_source(environment, template)
        except TemplateNotFound:
            basename = template.rsplit('/', 1)[-1]
            if basename == template:
                raise
            return super().get_source(environment, basename)


DEVELOPER_FOOTER = '''<!-- nagaram-developer-footer --><footer id="nagaram-developer-footer" style="width:100%;box-sizing:border-box;margin-top:32px;padding:16px 20px;text-align:center;background:#183f29;border-top:1px solid rgba(213,184,105,.35);color:#d8e4d5;font-family:inherit;font-size:12px;letter-spacing:.04em;line-height:1.5"><span>Web Developer: </span><strong style="color:#d5b869;font-weight:700">ARJUNE PRIYAN J</strong></footer>'''


def _initialize_schema(app):
    """Initialize storage without allowing a database outage to crash serverless import.

    Flask-SQLAlchemy sessions are scoped to an application context. Keep every
    session operation inside that context; a failed create_all must never call
    db.session.rollback() after the context has already been popped.
    """
    try:
        with app.app_context():
            try:
                db.create_all()
            except Exception:
                try:
                    db.session.rollback()
                except Exception:
                    pass
                raise
        app.config['DATABASE_READY'] = True
        app.config['DATABASE_INIT_ERROR'] = None
    except Exception as exc:
        app.config['DATABASE_READY'] = False
        app.config['DATABASE_INIT_ERROR'] = str(exc)
        app.logger.exception('NAGARAM database initialization failed; continuing in degraded mode')


def create_app():
    app = Flask(__name__, template_folder='.', static_folder=None)
    app.jinja_loader = RootTemplateLoader(app.root_path)
    app.config.from_object(Config)

    if os.environ.get('VERCEL'):
        app.instance_path = '/tmp/nagaram_instance'
        app.config['UPLOAD_FOLDER'] = '/tmp/nagaram_uploads'
    else:
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.root_path, filename)

    @app.route('/favicon.ico')
    @app.route('/favicon.png')
    def favicon():
        return b'', 204

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = None
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            return None

    from auth import auth_bp
    from citizen import citizen_bp
    from admin import admin_bp
    from ngo import ngo_bp
    from volunteer import volunteer_bp
    from safety import safety_bp
    from api import api_bp
    from main import main_bp
    from farmer import farmer_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(farmer_bp, url_prefix='/farmer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ngo_bp, url_prefix='/ngo')
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')
    app.register_blueprint(safety_bp, url_prefix='/safety')
    app.register_blueprint(api_bp, url_prefix='/api')

    _initialize_schema(app)

    @app.route('/healthz')
    def healthz():
        if not app.config.get('DATABASE_READY'):
            return jsonify({'status': 'degraded', 'service': 'nagaram', 'database': 'unavailable'}), 503
        try:
            db.session.query(User.id).limit(1).all()
            return jsonify({'status': 'ok', 'service': 'nagaram', 'storage': 'persistent' if Config.DATABASE_URL else 'temporary-preview'}), 200
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            return jsonify({'status': 'degraded', 'service': 'nagaram', 'database': 'unavailable'}), 503

    @app.after_request
    def add_developer_credit_and_prevent_caching(response):
        if response.mimetype == 'text/html' and response.status_code < 400:
            html = response.get_data(as_text=True)
            if 'nagaram-developer-footer' not in html:
                html = html.replace('</body>', DEVELOPER_FOOTER + '</body>', 1) if '</body>' in html else html + DEVELOPER_FOOTER
                response.set_data(html)
                response.headers['Content-Length'] = str(len(response.get_data()))
        response.headers['Cache-Control'] = 'private, no-store, max-age=0, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Vary'] = 'Cookie'
        return response

    @app.context_processor
    def inject_globals():
        unread_notifications = 0
        try:
            user = current_user._get_current_object()
            if getattr(user, 'is_authenticated', False):
                from models import Notification
                unread_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).count()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
        return {'unread_notifications': unread_notifications}

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except Exception:
            pass
        return render_template('500.html'), 500

    return app
