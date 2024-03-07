import sys

sys.dont_write_bytecode = True

from flask import request, jsonify
from app.models.user import User
from app.utils.jwt_utils import generate_token
from app import db
from app.models.user import User
from app.auth import auth_bp


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Expects a JSON payload with the following fields:
        - username (str): The user's username.
        - email (str): The user's email address.
        - password (str): The user's password.

    Returns:
        A JSON response with a success message or an error message.
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return jsonify({"error": "Username or email already taken"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in a user.

    Expects a JSON payload with the following fields:
        - username_or_email (str): The user's username or email address.
        - password (str): The user's password.

    Returns:
        A JSON response with a JSON Web Token or an error message.
    """
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")

    if not username_or_email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(password):
        return jsonify({"error": "Invalid username/email or password"}), 401

    token = generate_token(user.id)

    return jsonify({"token": token, "expiration": "Token is valid for 30 minutes"}), 200
