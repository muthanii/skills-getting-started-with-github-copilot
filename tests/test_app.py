from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client):
    # Arrange
    expected_activities = deepcopy(app_module.activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    participants_before = list(app_module.activities[activity_name]["participants"])
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert app_module.activities[activity_name]["participants"] == participants_before


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(signup_url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(signup_url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_not_found_for_non_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not-signed-up@mergington.edu"
    signup_url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"