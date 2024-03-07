import sys

sys.dont_write_bytecode = True

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    """
    Configuration class for the Flask application.

    Attributes:
        SECRET_KEY (str): The secret key used for securing the application.
        SQLALCHEMY_DATABASE_URI (str): The URI for the SQLite database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Whether to track modifications to the database models.
        JWT_SECRET_KEY (str): The secret key used for generating JSON Web Tokens.
    """

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
