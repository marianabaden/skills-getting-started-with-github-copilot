"""
Pytest configuration and shared fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for testing the FastAPI app.
    Creates a fresh client for each test to ensure isolation.
    """
    return TestClient(app)


@pytest.fixture
def mock_activities(monkeypatch):
    """
    Fixture that provides a fresh copy of mock activities data.
    Uses monkeypatch to replace the activities dict in the app module
    so that each test gets isolated data.
    """
    mock_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }
    
    # Replace the activities dict in the app module with our mock data
    import src.app
    original_activities = src.app.activities.copy()
    monkeypatch.setattr(src.app, "activities", mock_data)
    
    yield mock_data
    
    # Cleanup: restore original activities (if needed)
    monkeypatch.setattr(src.app, "activities", original_activities)
