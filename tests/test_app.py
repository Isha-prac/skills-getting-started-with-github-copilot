"""
Pytest tests for the Mergington High School API.
Tests follow the Arrange-Act-Assert pattern.
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    def test_root_redirects_to_static_index(self):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivitiesEndpoint:
    def test_get_activities_returns_activity_list(self):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert expected_activity in activities
        assert "description" in activities[expected_activity]
        assert "participants" in activities[expected_activity]


class TestSignupEndpoint:
    def test_signup_adds_new_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "testsignup@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

        # Cleanup
        client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

    def test_signup_duplicate_student_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipantEndpoint:
    def test_remove_existing_participant(self):
        # Arrange
        activity_name = "Programming Class"
        email = "removetest@mergington.edu"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

    def test_remove_nonexistent_participant_returns_404(self):
        # Arrange
        activity_name = "Basketball Team"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
