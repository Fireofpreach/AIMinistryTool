import os
import logging
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from modules.extensions import db  # Your SQLAlchemy instance

# Configure logging
logging.basicConfig(level=logging.DEBUG)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "eai-ministry-tool-secret-key")

    # Proxy fix (for correct url_for with HTTPS, etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///eai_ministry.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from modules.doctrine import doctrine_bp
    from modules.sermon import sermon_bp
    from modules.counseling import counseling_bp
    from modules.resources import resources_bp
    from modules.auth.routes import auth_bp  # <- Add this import

    app.register_blueprint(doctrine_bp, url_prefix='/doctrine')
    app.register_blueprint(sermon_bp, url_prefix='/sermon')
    app.register_blueprint(counseling_bp, url_prefix='/counseling')
    app.register_blueprint(resources_bp, url_prefix='/resources')
    app.register_blueprint(auth_bp)  # <- Register auth blueprint

    # Create database tables
    with app.app_context():
        import models  # noqa: F401
        db.create_all()
        logging.info("Database tables created successfully")

        # Add user_loader here so models import works
        @login_manager.user_loader
        def load_user(user_id):
            from models import User
            return User.query.get(int(user_id))

    # Optional: Add a simple root route
    @app.route('/')
    def index():
        return "Welcome to the EAI Ministry Tool API!"

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 so the app is reachable externally
    app.run(host="0.0.0.0", port=port, debug=True)
