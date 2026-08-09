import os

from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager, current_user
from jinja2 import FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from config import Config
from models import db, User


class RootTemplateLoader(FileSystemLoader):
    """Load the repository's flat template files even when routes use old paths."""

    def get_source(self, environment, template):
        try:
            return super().get_source(environment, template)
        except TemplateNotFound:
            basename = template.rsplit("/", 1)[-1]
            if basename == template:
                raise
            return super().get_source(environment, basename)


def create_app():
    # The repository keeps templates and frontend assets at the project root.
    # Do not use Flask's default ./templates and ./static directories.
    app = Flask(__name__, template_folder=".", static_folder=None)

    # Vercel's deployed filesystem is read-only except /tmp.
    if os.environ.get("VERCEL"):
        app.instance_path = "/tmp/urbanpulse_instance"
        os.makedirs(app.instance_path, exist_ok=True)

    # Support both the current flat template layout and older route references
    # such as "citizen/dashboard.html" without requiring every route module to
    # be rewritten at once.
    app.jinja_loader = RootTemplateLoader(app.root_path)

    app.config.from_object(Config)

    # Uploads must use /tmp on Vercel.
    if os.environ.get("VERCEL"):
        app.config["UPLOAD_FOLDER"] = "/tmp/urbanpulse_uploads"
    else:
        app.config["UPLOAD_FOLDER"] = os.path.join(
            app.root_path, "static", "uploads"
        )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # The project stores CSS/JS files at the repository root (for example
    # variables.css and app.js), while templates refer to /static/css/... and
    # /static/js/.... Map those logical paths to the existing root files.
    @app.route("/static/<path:filename>")
    def static_files(filename):
        if "/" in filename:
            filename = filename.rsplit("/", 1)[-1]
        return send_from_directory(app.root_path, filename)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except (TypeError, ValueError):
            return None

    # All route modules are at the repository root; there is no routes package.
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

    # Vercel imports run.py instead of executing it as __main__, so initialize
    # the schema here after all model modules have been imported.
    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_globals():
        unread_notifications = 0

        if current_user.is_authenticated:
            try:
                from models import Notification
                unread_notifications = Notification.query.filter_by(
                    user_id=current_user.id,
                    is_read=False
                ).count()
            except Exception:
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
