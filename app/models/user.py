import sys

sys.dont_write_bytecode = True

from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    Model class representing a user in the application.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The user's username.
        email (str): The user's email address.
        password_hash (str): The hashed password for the user.
        calorie_intakes (CalorieIntake): The relationship with the CalorieIntake model.
        calorie_charts (CalorieChart): The relationship with the CalorieCharts model.

    Methods:
        set_password(password): Set the password hash for the user.
        check_password(password): Check if the provided password matches the user's password hash.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    calorie_intakes = db.relationship("CalorieIntake", backref="user", lazy="dynamic")
    calorie_charts = db.relationship("CalorieChart", backref="user", lazy="dynamic")

    def set_password(self, password):
        """
        Set the password hash for the user.

        Args:
            password (str): The plain-text password to be hashed.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if the provided password matches the user's password hash.

        Args:
            password (str): The plain-text password to be checked.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
