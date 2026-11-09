
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Welcome to Expense Tracker API"
    }


def test_expenses_without_login():
    response = client.get("/expenses")

    assert response.status_code == 401


def test_budgets_without_login():
    response = client.get("/budgets")

    assert response.status_code == 401
