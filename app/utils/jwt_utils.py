import sys

sys.dont_write_bytecode = True

from flask import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from datetime import timedelta
from functools import wraps
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
import os

# Load environment variables from .env file
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


# Initialize the Fernet cipher suite with the secret key from environment variable
cipher_suite = Fernet(os.getenv("FERNET_SECRET_KEY"))


def encrypt(user_id):
    """
    Encrypt the user ID using Fernet encryption.

    Args:
        user_id (int): The user ID to encrypt.

    Returns:
        str: The encrypted user ID.
    """
    return cipher_suite.encrypt(str(user_id).encode()).decode()


def decrypt(encrypted_user_id):
    """
    Decrypt the encrypted user ID using Fernet decryption.

    Args:
        encrypted_user_id (str): The encrypted user ID to decrypt.

    Returns:
        int: The decrypted user ID.
    """
    return int(cipher_suite.decrypt(encrypted_user_id.encode()).decode())
