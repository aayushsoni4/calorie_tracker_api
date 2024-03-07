import sys

sys.dont_write_bytecode = True

from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from app.auth import routes
