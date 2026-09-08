"""
Test suite for Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest


# ============================================================================
# GET /activities Tests
# ============================================================================

class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client, mock_activities):
        """
        Arrange: Mock activities data is loaded via fixture
        Act: Send GET request to /activities
        Assert: Verify 200 status and response is a dict
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_all_fields(self, client, mock_activities):
        """
        Arrange: Mock activities data with known structure
        Act: Send GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert len(activities) > 0
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants_list_accurate(self, client, mock_activities):
        """
        Arrange: Mock data with known participants for specific activities
        Act: Send GET request to /activities
        Assert: Verify participants list matches arranged data
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert activities["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]
        assert activities["Programming Class"]["participants"] == ["emma@mergington.edu"]
        assert activities["Gym Class"]["participants"] == []


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, mock_activities):
        """
        Arrange: Mock data with a new email not yet signed up
        Act: Send POST request to signup
        Assert: Verify 200 status, success message, and participant added to list
        """
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in mock_activities[activity_name]["participants"]
    
    def test_signup_invalid_activity(self, client, mock_activities):
        """
        Arrange: Non-existent activity name
        Act: Send POST request with invalid activity
        Assert: Verify 404 status and "Activity not found" message
        """
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_email(self, client, mock_activities):
        """
        Arrange: Email already in activity's participants list
        Act: Send POST request with same email
        Assert: Verify 400 status and "already signed up" message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_updates_participant_list(self, client, mock_activities):
        """
        Arrange: New student email for empty activity
        Act: Send POST request to signup, then GET activities
        Assert: Verify participant appears in the updated activities list
        """
        # Arrange
        activity_name = "Gym Class"
        email = "alice@mergington.edu"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Fetch activities
        get_response = client.get("/activities")
        activities = get_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]


# ============================================================================
# DELETE /activities/{activity_name}/unregister Tests
# ============================================================================

class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, mock_activities):
        """
        Arrange: Participant in activity's participant list
        Act: Send DELETE request to unregister
        Assert: Verify 200 status, success message, and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in mock_activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in mock_activities[activity_name]["participants"]
    
    def test_unregister_invalid_activity(self, client, mock_activities):
        """
        Arrange: Non-existent activity name
        Act: Send DELETE request with invalid activity
        Assert: Verify 404 status and "Activity not found" message
        """
        # Arrange
        invalid_activity = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_non_existent_participant(self, client, mock_activities):
        """
        Arrange: Email not in activity's participants list
        Act: Send DELETE request for non-participant
        Assert: Verify 400 status and error message
        """
        # Arrange
        activity_name = "Gym Class"
        email = "notaparticipant@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_removes_from_list(self, client, mock_activities):
        """
        Arrange: Known participant in activity
        Act: Send DELETE request, then GET activities
        Assert: Verify participant no longer appears in activities response
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        assert email in mock_activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Act - Fetch activities
        get_response = client.get("/activities")
        activities = get_response.json()
        
        # Assert
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
