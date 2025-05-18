import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)

@pytest.fixture
def test_user():
    # Create a test user
    user_data = {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com"
    }
    
    # Delete the user if it already exists
    db.users.delete_one({"username": user_data["username"]})
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    
    token_data = response.json()
    return {
        "username": user_data["username"],
        "password": user_data["password"],
        "token": token_data["access_token"]
    }

def test_register_user():
    user_data = {
        "username": "newuser",
        "password": "newpassword",
        "email": "new@example.com"
    }
    
    # Delete the user if it already exists
    db.users.delete_one({"username": user_data["username"]})
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login(test_user):
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_start_pomodoro(test_user):
    headers = {
        "Authorization": f"Bearer {test_user['token']}"
    }
    
    response = client.post("/start-pomodoro", json={"duration": 25}, headers=headers)
    assert response.status_code == 200
    assert "end_time" in response.json()
    assert "audio_url" in response.json()
    assert "motivational_phrase" in response.json()

def test_complete_pomodoro(test_user):
    headers = {
        "Authorization": f"Bearer {test_user['token']}"
    }
    
    response = client.post("/complete-pomodoro", headers=headers)
    assert response.status_code == 200
    assert "message" in response.json()
    assert "tree" in response.json()
    
    tree = response.json()["tree"]
    assert "id" in tree
    assert "name" in tree
    assert "category" in tree
    assert "image_url" in tree
    assert "description" in tree
    
    # Save the tree ID for next test
    test_user["tree_id"] = tree["id"]
    
    return tree

def test_get_trees(test_user):
    headers = {
        "Authorization": f"Bearer {test_user['token']}"
    }
    
    response = client.get("/trees", headers=headers)
    assert response.status_code == 200
    
    # Should have at least one tree from previous test
    trees = response.json()
    assert len(trees) > 0

def test_update_tree(test_user):
    # First make sure we have a tree
    tree = test_complete_pomodoro(test_user)
    
    headers = {
        "Authorization": f"Bearer {test_user['token']}"
    }
    
    updated_tree = {
        "name": "Updated Tree Name",
        "category": tree["category"],
        "image_url": tree["image_url"],
        "description": "Updated description"
    }
    
    response = client.put(f"/trees/{tree['id']}", json=updated_tree, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Tree updated successfully"

def test_delete_tree(test_user):
    # First make sure we have a tree
    tree = test_complete_pomodoro(test_user)
    
    headers = {
        "Authorization": f"Bearer {test_user['token']}"
    }
    
    response = client.delete(f"/trees/{tree['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Tree deleted successfully"
