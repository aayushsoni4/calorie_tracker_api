import sys

sys.dont_write_bytecode = True

from flask import request, jsonify, make_response, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.calorie_intake import CalorieIntake
from app.models.calorie_charts import CalorieChart
from app.models.user import User
from app import db
import pandas as pd
from datetime import datetime, timedelta
from app.utils.charts_utils import generate_calorie_chart_pdf
from app.utils.jwt_utils import encrypt, decrypt
from app.main import main_bp
from io import StringIO


@main_bp.route("/intake", methods=["POST"])
@jwt_required()
def create_intake():
    """
    Create calorie intake record(s).

    Expects a JSON payload with either a single entry or multiple entries.

    Returns:
        A JSON response with a success message or an error message.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not isinstance(data, list):
        # If the payload is not a list, assume it's a single entry
        data = [data]

    for entry in data:
        calories = entry.get("calories")
        date_str = entry.get("date")

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        existing_intake = CalorieIntake.query.filter_by(
            user_id=user_id, date=date
        ).first()

        if existing_intake:
            # If an intake record for the same date already exists, update the calories
            existing_intake.calories += calories
        else:
            # If no intake record for the same date exists, create a new record
            intake = CalorieIntake(user_id=user_id, date=date, calories=calories)
            db.session.add(intake)

    db.session.commit()

    return jsonify({"message": "Calorie intake recorded"}), 201


@main_bp.route("/intake", methods=["GET"])
@jwt_required()
def get_intakes():
    """
    Retrieve calorie intake records for the authenticated user.

    Accepts optional query parameters:
        - start_date (str): The start date in the format YYYY-MM-DD.
        - end_date (str): The end date in the format YYYY-MM-DD.

    Returns:
        A JSON response with the calorie intake records or an error message.
    """
    user_id = get_jwt_identity()
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    try:
        start_date = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str
            else None
        )
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        )
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    query = CalorieIntake.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(CalorieIntake.date >= start_date)
    if end_date:
        query = query.filter(CalorieIntake.date <= end_date)

    query = query.order_by(CalorieIntake.date.desc())

    intakes = [
        {"date": intake.date.isoformat(), "calories": intake.calories}
        for intake in query.all()
    ]

    return jsonify(intakes), 200


@main_bp.route("/chart", methods=["GET"])
@jwt_required()
def get_calorie_chart():
    """
    Generate and retrieve a PDF report with a calorie intake chart.

    Accepts optional query parameters:
        - start_date (str): The start date in the format YYYY-MM-DD.
        - end_date (str): The end date in the format YYYY-MM-DD.

    Returns:
        A JSON response containing the URL to download the PDF file or an error message.
    """
    user_id = get_jwt_identity()
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    try:
        start_date = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str
            else None
        )
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        )
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    query = CalorieIntake.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(CalorieIntake.date >= start_date)
    if end_date:
        query = query.filter(CalorieIntake.date <= end_date)

    query = query.order_by(CalorieIntake.date.desc())
    data = [
        {"Date": intake.date.strftime("%Y-%m-%d"), "Calories": intake.calories}
        for intake in query.all()
    ]

    df = pd.DataFrame(data)
    pdf_content = generate_calorie_chart_pdf(df)

    # Save the PDF content to the database
    calorie_pdf = CalorieChart.query.filter_by(user_id=user_id).first()
    if calorie_pdf:
        # If entry already exists, update the PDF content
        calorie_pdf.pdf = pdf_content
    else:
        # Otherwise, create a new entry
        calorie_pdf = CalorieChart(user_id=user_id, pdf=pdf_content)
        db.session.add(calorie_pdf)
    db.session.commit()

    # Construct the URL to download the PDF file
    pdf_url = url_for(
        "main.download_calorie_pdf", user_id=encrypt(user_id), _external=True
    )

    # Create JSON response with the URL
    response_data = {"pdf_url": pdf_url, "message": "PDF file generated successfully."}
    return jsonify(response_data), 200


@main_bp.route("/download_pdf", methods=["GET"])
def download_calorie_pdf():
    # Retrieve the encrypted user_id from the query parameter
    encrypted_user_id = request.args.get("user_id")

    # Decrypt the encrypted user_id
    try:
        user_id = decrypt(encrypted_user_id)
    except Exception as e:
        return jsonify({"error": "Invalid encrypted user_id"}), 400

    # Retrieve the PDF content from the database
    calorie_pdf = CalorieChart.query.filter_by(user_id=user_id).first()
    if not calorie_pdf:
        return jsonify({"error": "No PDF data found for the user"}), 404

    pdf_bytes = calorie_pdf.pdf

    # Send the bytes using send_file
    response = make_response(pdf_bytes)
    response.headers["Content-Disposition"] = "attachment; filename=calorie_chart.pdf"
    response.mimetype = "application/pdf"
    return response


@main_bp.route("/csv", methods=["GET"])
@jwt_required()
def get_calorie_csv():
    """
    Generate and retrieve a CSV file with calorie intake data.

    Accepts optional query parameters:
        - start_date (str): The start date in the format YYYY-MM-DD.
        - end_date (str): The end date in the format YYYY-MM-DD.

    Returns:
        A JSON response containing the URL to download the CSV file or an error message.
    """
    user_id = get_jwt_identity()  # Get user ID from JWT token
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    try:
        start_date = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str
            else None
        )
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        )
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    query = CalorieIntake.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(CalorieIntake.date >= start_date)
    if end_date:
        query = query.filter(CalorieIntake.date <= end_date)

    query = query.order_by(CalorieIntake.date.desc())

    data = [
        {"Date": intake.date.strftime("%Y-%m-%d"), "Calories": intake.calories}
        for intake in query.all()
    ]
    df = pd.DataFrame(data)

    csv_content = StringIO()
    df.to_csv(csv_content, index=False)

    csv_content.seek(
        0
    )  # Reset the file pointer to the beginning of the StringIO buffer
    csv_bytes = csv_content.getvalue().encode("utf-8")

    # Save CSV content to the database
    calorie_chart = CalorieChart.query.filter_by(user_id=user_id).first()
    if calorie_chart:
        # If entry already exists, update the CSV content
        calorie_chart.csv = csv_bytes
    else:
        # Otherwise, create a new entry
        calorie_chart = CalorieChart(user_id=user_id, csv=csv_bytes)
        db.session.add(calorie_chart)
    db.session.commit()

    # Retrieve the CSV content from the database
    calorie_chart = CalorieChart.query.filter_by(user_id=user_id).first()
    if not calorie_chart:
        return jsonify({"error": "No CSV data found for the user"}), 404

    csv_bytes = calorie_chart.csv

    # Construct the URL to download the CSV file
    csv_url = url_for(
        "main.download_calorie_csv", user_id=encrypt(user_id), _external=True
    )

    # Create JSON response with the URL
    response_data = {"csv_url": csv_url, "message": "CSV file generated successfully."}

    return jsonify(response_data), 200


@main_bp.route("/download_csv", methods=["GET"])
def download_calorie_csv():
    # Retrieve the user_id from the query parameters
    encrypted_user_id = request.args.get("user_id")

    # Decrypt the encrypted user_id
    try:
        user_id = decrypt(encrypted_user_id)
    except Exception as e:
        return jsonify({"error": "Invalid encrypted user_id"}), 400

    # Check if user_id is provided
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 400

    # Retrieve the CSV content from the database
    calorie_chart = CalorieChart.query.filter_by(user_id=user_id).first()
    if not calorie_chart:
        return jsonify({"error": "No CSV data found for the user"}), 404

    csv_bytes = calorie_chart.csv

    # Send the bytes using send_file
    response = make_response(csv_bytes)
    response.headers["Content-Disposition"] = "attachment; filename=calorie_data.csv"
    response.mimetype = "text/csv"

    return response


@main_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """
    Retrieves the profile of the currently authenticated user.

    Requires a valid JWT token in the Authorization header.

    Returns:
        A JSON response with the user's profile information or an error message.
    """
    # Retrieve the current user's ID from the JWT token
    current_user_id = get_jwt_identity()

    # Query the database to retrieve the user's profile
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Calculate the token's expiration time
    exp_timestamp = get_jwt()["exp"]
    exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
    expires_in = exp_datetime - datetime.utcnow()

    # Calculate the token's expiration time in minutes and seconds
    total_seconds = expires_in.total_seconds()
    minutes, seconds = divmod(total_seconds, 60)

    # Prepare the response JSON with user profile information and token expiration time
    user_profile = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "token_expires_in": f"{int(minutes)} mins {int(seconds)} secs"
    }

    return jsonify(user_profile), 200
