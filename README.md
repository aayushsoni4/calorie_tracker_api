# Calories Tracker

The Calories Tracker is a web application designed to help users monitor their daily calorie intake and manage their nutrition effectively. This document provides comprehensive documentation on installation, usage, and API endpoints for interacting with the application.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)

## Installation

To set up the Calories Tracker application locally, follow these instructions:

1. Navigate to the project directory:

   ```bash
   cd calories-tracker
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the development server:

   ```bash
   python run.py
   ```

The application should now be running locally at `http://localhost:5000`.

## Usage

To use the Calories Tracker application, follow these steps:

1. Register a new user using the `/auth/register` endpoint.
2. Log in to the application using the `/auth/login` endpoint to obtain an authentication token.
3. Use the obtained token to access protected endpoints such as `/user/profile`.
4. Input daily calorie intake using the provided endpoints.
5. View and manage user profile information and calorie intake logs.

## API Documentation

### Authentication

#### Register a User

Registers a new user with the application.

- **Endpoint**: `/auth/register`
- **Method**: `POST`
- **Request Body**:

  ```json
  {
    "username": "example_user",
    "password": "password123",
    "email": "example@example.com"
  }
  ```

  - **Success Response**:

    - **Status Code**: `201 Created`
    - **Body**:

      ```json
      {
        "message": "User registered successfully",
        "user_id": 123
      }
      ```

  - **Error Responses**:
    - **Status Code**: `400 Bad Request`
      - Invalid request format or missing required fields.

#### Login

Logs in a user and returns an authentication token.

- **Endpoint**: `/auth/login`
- **Method**: `POST`
- **Request Body**:

  ```json
  {
    "username_or_email": "example_user",
    "password": "password123"
  }
  ```

  - **Success Response**:

    - **Status Code**: `200 OK`
    - **Body**:

      ```json
      {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjM0NTY3ODkwLCJ1c2VybmFtZSI6ImV4YW1wbGVfdXNlciIsImV4cCI6MTY0NTc5MTUyNX0.Jcf1onmI6NlO8yLoYOjgZVeZThf4FakXoZ-tiPs1n9w",
        "expiration": "Token is valid for 30 minutes"
      }
      ```

  - **Error Responses**:
    - **Status Code**: `401 Unauthorized`
      - Missing or invalid authentication token.
    - **Status Code**: `404 Not Found`
      - Resource not found.
    - **Status Code**: `500 Internal Server Error`
      - Unexpected server error.

  Now, users will be informed that the authentication token is valid for `30 minutes` upon successful login.

### User Calorie Intake Management

#### Add Calorie Intake

Adds daily calorie intake for the authenticated user.

- **Endpoint**: `/user/intake`
- **Method**: `POST`
- **Authorization Header**: `Bearer <token>`
- **Request Body**:

  ```json
  [
    {
      "date": "YYYY-MM-DD",
      "calories": 1500
    },
    {
      "date": "YYYY-MM-DD",
      "calories": 1800
    }
  ]
  ```

  or

  ```json
  {
    "date": "YYYY-MM-DD",
    "calories": 1500
  }
  ```

  - **Success Response**:

    - **Status Code**: `200 OK`
    - **Body**:

      ```json
      {
        "message": "Calorie intake recorded"
      }
      ```

  - **Error Responses**:
    - **Status Code**: `400 Bad Request`
      - Invalid request format or missing required fields.

#### Get Calorie Intake

Retrieves the daily calorie intake for the authenticated user.

- **Endpoint**: `/user/intake`
- **Method**: `GET`
- **Authorization Header**: `Bearer <token>`
- **Response**: List of JSON objects containing date and calorie intake.

#### User Profile

#### Get User Profile

Retrieves the profile of the currently authenticated user.

- **Endpoint**: `/user/profile`
- **Method**: `GET`
- **Authorization Header**: `Bearer <token>`
- **Response**:

  ```json
  {
    "user_id": 123,
    "username": "example_user",
    "email": "example@example.com"
  }
  ```

### Data Export

#### Export Calorie Intake Data as CSV

Exports the user's calorie intake data as a CSV file.

- **Endpoint**: `/user/csv`
- **Method**: `GET`
- **Authorization Header**: `Bearer <token>`
- **Response**: Success message with a download link.

#### Export Calorie Intake Data as Chart

Exports the user's calorie intake data as a chart image.

- **Endpoint**: `/user/chart`
- **Method**: `GET`
- **Authorization Header**: `Bearer <token>`
- **Response**: Success message with a download link.
