import sys

sys.dont_write_bytecode = True

from flask import Blueprint

main_bp = Blueprint("main", __name__)

from app.main import routes