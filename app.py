import logging
import os

from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from modules.extensions import db  # Your custom SQLAlchemy with Base

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "eai-ministry-tool-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///eai_ministry.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import blueprints
from modules.doctrine import doctrine_bp
from modules.sermon import sermon_bp
from modules.counseling import counseling_bp
from modules.resources import resources_bp

# Register blueprints
app.register_blueprint(doctrine_bp, url_prefix='/doctrine')
app.register_blueprint(sermon_bp, url_prefix='/sermon')
app.register_blueprint(counseling_bp, url_prefix='/counseling')
app.register_blueprint(resources_bp, url_prefix='/resources')

# Create tables
with app.app_context():
    # Import models
    import models  # noqa: F401

    db.create_all()
    logging.info("Database tables created successfully")

# Import routes
from routes import *  # noqa: F401, E402

