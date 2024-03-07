import sys

sys.dont_write_bytecode = True

from app import db


class CalorieChart(db.Model):
    """
    Model class representing PDF and CSV calorie charts for a user.

    Attributes:
        id (int): The unique identifier for the calorie chart.
        user_id (int): The ID of the user associated with the calorie chart.
        pdf (blob): PDF file of the calorie chart.
        csv (blob): CSV file of the calorie chart.

    Methods:
        __repr__(): Return a string representation of the CalorieCharts instance.
    """

    __tablename__ = "calorie_charts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pdf = db.Column(db.BLOB)
    csv = db.Column(db.BLOB)

    def __repr__(self):
        return f"<CalorieCharts id:{self.id}>"
