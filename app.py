import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, current_user
from config import Config
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.citizen import citizen_bp
    from routes.admin import admin_bp
    from routes.ngo import ngo_bp
    from routes.volunteer import volunteer_bp
    from routes.safety import safety_bp
    from routes.api import api_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ngo_bp, url_prefix='/ngo')
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')
    app.register_blueprint(safety_bp, url_prefix='/safety')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.context_processor
    def inject_globals():
        unread_notifications = 0
        if current_user.is_authenticated:
            from models import Notification
            unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_notifications=unread_notifications)

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
