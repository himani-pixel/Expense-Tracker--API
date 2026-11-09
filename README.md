# Expense Tracker API

A backend-focused Expense Tracker application built using Python, FastAPI, MySQL and SQLAlchemy.

## Features

- User Registration and Login
- JWT Authentication
- Password Hashing
- Add, View, Update and Delete Expenses
- Expense Categories
- Monthly Budget Management
- Category-wise Expense Reports
- Monthly Expense Reports
- Budget Status Tracking

## Tech Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- Pydantic
- JWT Authentication
- Git and GitHub

## Project Structure

```text
expense-tracker-api/
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── user_schemas.py
│   ├── budget_schemas.py
│   └── test_db.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your MySQL database URL and JWT configuration.
5. Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

## API Documentation

Open the following URL after starting the server:

`http://127.0.0.1:8000/docs`

## Database

MySQL is used to store user accounts, expenses, categories and budgets.

## Project Status

Backend development and API testing in progress.