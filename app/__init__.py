from flask import Flask, render_template # render_template might be needed if we keep a simple index here
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from datetime import datetime # Import datetime
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message_category = 'info' # Use a bootstrap category for login_required flash message

def create_app(config_class=Config):
    app = Flask(__name__)
    csrf.init_app(app)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.cylinders import bp as cylinders_bp
    app.register_blueprint(cylinders_bp, url_prefix='/cylinders')

    from app.routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.routes.main import bp as main_bp # New main blueprint
    app.register_blueprint(main_bp) # Register without prefix for '/'

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback() # Rollback db session in case of error
        return render_template('errors/500.html', title='Internal Server Error'), 500

    return app
