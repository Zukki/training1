"""Test cases for the High School Management System API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_state = {
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
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_state)


class TestSignupForActivity:
    """Test suite for signup_for_activity function"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert response.json() == {
            "message": "Signed up alice@mergington.edu for Chess Club"
        }
        assert "alice@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities["Programming Class"]["participants"]
        assert email2 in activities["Programming Class"]["participants"]
    
    def test_signup_preserves_existing_participants(self, client, reset_activities):
        """Test that signup preserves existing participants"""
        original_participants = activities["Gym Class"]["participants"].copy()
        
        response = client.post(
            "/activities/Gym%20Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        # Verify all original participants are still there
        for participant in original_participants:
            assert participant in activities["Gym Class"]["participants"]
        # Verify new participant was added
        assert "newstudent@mergington.edu" in activities["Gym Class"]["participants"]
