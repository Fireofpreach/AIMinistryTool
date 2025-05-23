import logging
import os

from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from modules.extensions import db  # Shared SQLAlchemy instance

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory function"""

    app = Flask(__name__)

    # Secret key for sessions
    app.secret_key = os.environ.get("SESSION_SECRET", "eai-ministry-tool-secret-key")

    # Middleware to handle proxied requests (e.g., HTTPS behind proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///eai_ministry.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize extensions with app
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Adjust to your auth blueprint's login route

    # Import and register blueprints
    from modules.doctrine import doctrine_bp
    from modules.sermon import sermon_bp
    from modules.counseling import counseling_bp
    from modules.resources import resources_bp

    app.register_blueprint(doctrine_bp, url_prefix='/doctrine')
    app.register_blueprint(sermon_bp, url_prefix='/sermon')
    app.register_blueprint(counseling_bp, url_prefix='/counseling')
    app.register_blueprint(resources_bp, url_prefix='/resources')

    # Create tables on app start
    with app.app_context():
        import models  # noqa: F401 to register models with SQLAlchemy
        db.create_all()
        logger.info("Database tables created successfully")

    # Import routes if you have any additional routes outside blueprints
    # from routes import *  # noqa: F401, E402

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
