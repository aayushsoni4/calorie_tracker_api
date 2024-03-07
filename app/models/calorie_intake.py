import sys

sys.dont_write_bytecode = True

from app import db
from datetime import date


class CalorieIntake(db.Model):
    """
    Model class representing a daily calorie intake record for a user.

    Attributes:
        id (int): The unique identifier for the calorie intake record.
        user_id (int): The ID of the user associated with the calorie intake record.
        date (date): The date of the calorie intake record.
        calories (int): The number of calories consumed on the specified date.

    Methods:
        __repr__(): Return a string representation of the CalorieIntake instance.
    """

    __tablename__ = "calorie_intakes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    calories = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<CalorieIntake {self.date.isoformat()} - {self.calories} calories>"
