import copy
from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of the activities before each test and restore after
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Football Club" in data
    assert isinstance(data["Football Club"]["participants"], list)


def test_signup_and_unregister_flow():
    email = "temp@example.com"
    activity = "Football Club"

    # Sign up
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Participant should be in the activity
    assert email in activities[activity]["participants"]

    # Unregister
    res = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 200
    assert "Unregistered" in res.json().get("message", "")

    # Participant should be removed
    assert email not in activities[activity]["participants"]


def test_signup_existing():
    activity = "Football Club"
    email = "alex@mergington.edu"  # already present
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 400
    assert "already signed up" in res.json().get("detail", "").lower()


def test_unregister_not_found():
    activity = "Football Club"
    email = "notfound@example.com"

    # Ensure the participant is not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    res = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res.status_code == 404
