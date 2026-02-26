"""
Flask app factory for Newsletter Distiller
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_name='development'):
    """Create and configure the Flask app."""
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'production':
        from config import ProductionConfig as config
    else:
        from config import DevelopmentConfig as config
    
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.gmail import gmail_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(gmail_bp)
    
    return app
