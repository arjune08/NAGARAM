import os

from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager, current_user
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from config import Config
from models import db, User


class RootTemplateLoader(FileSystemLoader):
    def get_source(self, environment, template):
        try:
            return super().get_source(environment, template)
        except TemplateNotFound:
            basename = template.rsplit("/", 1)[-1]
            if basename == template:
                raise
            return super().get_source(environment, basename)


def create_app():
    app = Flask(__name__, template_folder=".", static_folder=None)
    app.jinja_loader = RootTemplateLoader(app.root_path)
    app.config.from_object(Config)

    if os.environ.get("VERCEL"):
        app.instance_path = "/tmp/urbanpulse_instance"
        app.config["UPLOAD_FOLDER"] = "/tmp/urbanpulse_uploads"
    else:
        app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.route("/static/<path:filename>")
    def static_files(filename):
        filename = filename.rsplit("/", 1)[-1]
        return send_from_directory(app.root_path, filename)

    @app.route("/favicon.ico")
    @app.route("/favicon.png")
    def favicon():
        return (b"", 204)

    # Never boot a Vercel function against SQLite. If the persistent database
    # URL is missing, fail with a clear configuration error rather than letting
    # users log in against a temporary database that disappears between
    # serverless instances.
    if os.environ.get("VERCEL") and not Config.DATABASE_URL:
        raise RuntimeError(
            "Nagaram production database is not configured. "
            "Set DATABASE_URL in Vercel Production to the Neon PostgreSQL URL."
        )

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None
        except Exception:
            db.session.rollback()
            return None

    from auth import auth_bp
    from citizen import citizen_bp
    from admin import admin_bp
    from ngo import ngo_bp
    from volunteer import volunteer_bp
    from safety import safety_bp
    from api import api_bp
    from main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(citizen_bp, url_prefix="/citizen")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(ngo_bp, url_prefix="/ngo")
    app.register_blueprint(volunteer_bp, url_prefix="/volunteer")
    app.register_blueprint(safety_bp, url_prefix="/safety")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Neon is persistent. CREATE TABLE IF NOT EXISTS makes first deployment
    # self-initializing without relying on a writable Vercel filesystem.
    if Config.DATABASE_URL:
        with app.app_context():
            db.create_all()

    @app.context_processor
    def inject_globals():
        unread_notifications = 0
        if current_user.is_authenticated:
            try:
                from models import Notification
                unread_notifications = Notification.query.filter_by(
                    user_id=current_user.id, is_read=False
                ).count()
            except Exception:
                db.session.rollback()
                unread_notifications = 0
        return {"unread_notifications": unread_notifications}

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app
