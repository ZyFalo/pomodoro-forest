from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Pomodoro Forest API"}
