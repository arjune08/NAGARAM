import os
from flask import Flask, jsonify, render_template, send_from_directory, session
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
        """Serve the repository's flat static assets.

        The project historically used both ``/static/foo.css`` and
        ``/static/css/foo.css`` style URLs. The repository stores CSS/JS at
        its root, so accept both forms to keep older templates working while
        new templates use the canonical root asset names.
        """
        normalized = filename.replace('\\', '/')
        for prefix in ('css/', 'js/'):
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        return send_from_directory(app.root_path, normalized)

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

    def _restore_supabase_user():
        """Rebuild the local Flask user when a Vercel instance lost /tmp storage.
        Supabase remains the source of truth for the authenticated identity.
        """
        access_token = session.get('supabase_access_token')
        refresh_token = session.get('supabase_refresh_token')
        if not access_token and not refresh_token:
            return None
        try:
            from supabase_auth import get_user, refresh_session, SupabaseAuthError
            try:
                remote_user = get_user(access_token) if access_token else None
            except SupabaseAuthError:
                refreshed = refresh_session(refresh_token)
                session['supabase_access_token'] = refreshed.get('access_token', '')
                session['supabase_refresh_token'] = refreshed.get('refresh_token', refresh_token)
                session['supabase_user_id'] = (refreshed.get('user') or {}).get('id', session.get('supabase_user_id', ''))
                remote_user = refreshed.get('user') or get_user(session.get('supabase_access_token'))

            if not remote_user:
                return None
            email = (remote_user.get('email') or session.get('supabase_email') or '').strip().lower()
            if not email:
                return None
            metadata = remote_user.get('user_metadata') or session.get('supabase_metadata') or {}
            user = User.query.filter_by(email=email).first()
            if user is None:
                user = User(
                    full_name=metadata.get('full_name') or email.split('@')[0],
                    email=email,
                    role=metadata.get('role') or 'citizen',
                    phone=metadata.get('phone') or ''
                )
                user.set_password(os.urandom(32).hex())
                db.session.add(user)
                db.session.flush()
                if user.role == 'farmer':
                    from farmer_models import FarmerProfile
                    db.session.add(FarmerProfile(
                        user_id=user.id,
                        village=metadata.get('village') or 'Demo Gram',
                        district=metadata.get('district') or '',
                        preferred_language=metadata.get('preferred_language') or 'en'
                    ))
                db.session.commit()
            session['supabase_email'] = email
            session['supabase_metadata'] = metadata
            session['_user_id'] = str(user.id)
            session['_fresh'] = False
            session.permanent = True
            session.modified = True
            return user
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            return None

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = db.session.get(User, int(user_id))
            if user is not None:
                return user
        except (TypeError, ValueError):
            return None
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
        return _restore_supabase_user()

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
