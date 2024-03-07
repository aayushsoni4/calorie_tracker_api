import sys

sys.dont_write_bytecode = True

from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta
from functools import wraps
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
import os

load_dotenv()


def generate_token(user_id):
    """
    Generate a JSON Web Token (JWT) for the given user ID.

    Args:
        user_id (int): The ID of the user to generate the token for.

    Returns:
        str: The generated JWT token.
    """
    access_token = create_access_token(
        identity=user_id, expires_delta=timedelta(minutes=30)
    )
    return access_token


def jwt_required(func):
    """
    Decorator function to protect routes and ensure that only authenticated users can access them.

    Args:
        func (callable): The route function to be decorated.

    Returns:
        callable: The decorated route function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            get_jwt_identity()
        except:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)

    return wrapper


cipher_suite = Fernet("zQnZn0OLUGF7ob5bSw3zcw2mYy3_oqKm5BBb5R3TnNo=")


# Encrypt the user_id
def encrypt(user_id):
    return cipher_suite.encrypt(str(user_id).encode()).decode()


# Decrypt the encrypted user_id
def decrypt(encrypted_user_id):
    return int(cipher_suite.decrypt(encrypted_user_id.encode()).decode())
