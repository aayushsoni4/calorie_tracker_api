import sys

sys.dont_write_bytecode = True

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    Args:
        config_class (Config): The configuration class for the application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import main_bp

    app.register_blueprint(main_bp, url_prefix="/user")

    return app
