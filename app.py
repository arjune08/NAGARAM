```python
import os

from flask import Flask, render_template
from flask_login import LoginManager, current_user

from config import Config
from models import db, User


def create_app():
    # ---------------------------------------------------------
    # Create Flask application
    # ---------------------------------------------------------
    app = Flask(__name__)

    # ---------------------------------------------------------
    # Vercel writable instance directory
    # IMPORTANT:
    # This must be set BEFORE db.init_app(app)
    # ---------------------------------------------------------
    if os.environ.get("VERCEL"):
        app.instance_path = "/tmp/urbanpulse_instance"

    # Load application configuration
    app.config.from_object(Config)

    # ---------------------------------------------------------
    # Upload directory
    # Vercel filesystem is read-only except /tmp
    # ---------------------------------------------------------
    if os.environ.get("VERCEL"):
        app.config["UPLOAD_FOLDER"] = "/tmp/urbanpulse_uploads"
    else:
        app.config["UPLOAD_FOLDER"] = os.path.join(
            app.root_path,
            "static",
            "uploads"
        )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    db.init_app(app)

    # ---------------------------------------------------------
    # Login manager
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Register blueprints
    #
    # IMPORTANT:
    # Your repository has these files at the ROOT level.
    # There is NO "routes" package.
    # ---------------------------------------------------------
    from auth import auth_bp
    from citizen import citizen_bp
    from admin import admin_bp
    from ngo import ngo_bp
    from volunteer import volunteer_bp
    from safety import safety_bp
    from api import api_bp
    from main import main_bp

    app.register_blueprint(
        main_bp
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/auth"
    )

    app.register_blueprint(
        citizen_bp,
        url_prefix="/citizen"
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin"
    )

    app.register_blueprint(
        ngo_bp,
        url_prefix="/ngo"
    )

    app.register_blueprint(
        volunteer_bp,
        url_prefix="/volunteer"
    )

    app.register_blueprint(
        safety_bp,
        url_prefix="/safety"
    )

    app.register_blueprint(
        api_bp,
        url_prefix="/api"
    )

    # ---------------------------------------------------------
    # Global template variables
    # ---------------------------------------------------------
    @app.context_processor
    def inject_globals():

        unread_notifications = 0

        if current_user.is_authenticated:
            try:
                from models import Notification

                unread_notifications = (
                    Notification.query
                    .filter_by(
                        user_id=current_user.id,
                        is_read=False
                    )
                    .count()
                )
            except Exception:
                # Prevent notification errors from crashing
                # the entire application.
                unread_notifications = 0

        return {
            "unread_notifications": unread_notifications
        }

    # ---------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template(
            "errors/403.html"
        ), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            "errors/404.html"
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()

        return render_template(
            "errors/500.html"
        ), 500

    return app
```
