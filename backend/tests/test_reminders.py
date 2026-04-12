"""Tests for reminder CRUD endpoints"""
import pytest
from httpx import AsyncClient

from app.models.user import User
from app.models.reminder import Reminder, UseCaseTemplate


@pytest.mark.asyncio
async def test_list_reminders_empty(
    client: AsyncClient,
    test_session_id: str
):
    """Test listing reminders when user has none"""
    response = await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_reminders_with_data(
    client: AsyncClient,
    test_db,
    test_user: User,
    test_session_id: str
):
    """Test listing reminders returns user's active reminders"""
    # Create test reminders
    reminder1 = Reminder(
        user_id=test_user.id,
        condition="rain",
        hours_ahead=6,
        is_active=True
    )
    reminder2 = Reminder(
        user_id=test_user.id,
        condition="snow",
        hours_ahead=12,
        is_active=True
    )
    reminder3 = Reminder(
        user_id=test_user.id,
        condition="hot",
        hours_ahead=24,
        is_active=False  # Inactive, should not appear
    )

    test_db.add_all([reminder1, reminder2, reminder3])
    await test_db.commit()

    response = await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Only active reminders
    assert all(r["is_active"] for r in data)


@pytest.mark.asyncio
async def test_list_reminders_pagination(
    client: AsyncClient,
    test_db,
    test_user: User,
    test_session_id: str
):
    """Test reminder pagination"""
    # Create 10 test reminders
    for i in range(10):
        reminder = Reminder(
            user_id=test_user.id,
            condition=f"condition{i}",
            hours_ahead=6,
            is_active=True
        )
        test_db.add(reminder)
    await test_db.commit()

    # Get first page (limit=5)
    response = await client.get(
        "/api/reminders/?limit=5&offset=0",
        headers={"X-Session-ID": test_session_id}
    )
    assert response.status_code == 200
    assert len(response.json()) == 5

    # Get second page
    response = await client.get(
        "/api/reminders/?limit=5&offset=5",
        headers={"X-Session-ID": test_session_id}
    )
    assert response.status_code == 200
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_create_reminder_success(
    client: AsyncClient,
    test_session_id: str
):
    """Test creating a reminder successfully"""
    reminder_data = {
        "condition": "rain",
        "hours_ahead": 6,
        "custom_message": "Don't forget umbrella!"
    }

    response = await client.post(
        "/api/reminders/",
        json=reminder_data,
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["condition"] == "rain"
    assert data["hours_ahead"] == 6
    assert data["custom_message"] == "Don't forget umbrella!"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_create_reminder_with_template(
    client: AsyncClient,
    test_template: UseCaseTemplate,
    test_session_id: str
):
    """Test creating a reminder with a template reference"""
    reminder_data = {
        "condition": "rain",
        "hours_ahead": 6,
        "template_id": test_template.id
    }

    response = await client.post(
        "/api/reminders/",
        json=reminder_data,
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["template_id"] == test_template.id


@pytest.mark.asyncio
async def test_create_reminder_invalid_template(
    client: AsyncClient,
    test_session_id: str
):
    """Test creating a reminder with non-existent template fails"""
    reminder_data = {
        "condition": "rain",
        "hours_ahead": 6,
        "template_id": 99999  # Non-existent
    }

    response = await client.post(
        "/api/reminders/",
        json=reminder_data,
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_reminder_validation(
    client: AsyncClient,
    test_session_id: str
):
    """Test reminder validation"""
    # Test missing fields
    response = await client.post(
        "/api/reminders/",
        json={},
        headers={"X-Session-ID": test_session_id}
    )
    assert response.status_code == 422

    # Test invalid hours_ahead (too high)
    response = await client.post(
        "/api/reminders/",
        json={"condition": "rain", "hours_ahead": 200},
        headers={"X-Session-ID": test_session_id}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_reminder_unauthenticated(client: AsyncClient):
    """Test creating a reminder without authentication fails"""
    reminder_data = {
        "condition": "rain",
        "hours_ahead": 6
    }

    response = await client.post(
        "/api/reminders/",
        json=reminder_data
    )

    assert response.status_code == 422  # Missing header


@pytest.mark.asyncio
async def test_delete_reminder_success(
    client: AsyncClient,
    test_db,
    test_user: User,
    test_session_id: str
):
    """Test soft deleting a reminder"""
    # Create reminder
    reminder = Reminder(
        user_id=test_user.id,
        condition="rain",
        hours_ahead=6,
        is_active=True
    )
    test_db.add(reminder)
    await test_db.commit()
    await test_db.refresh(reminder)

    # Delete reminder
    response = await client.delete(
        f"/api/reminders/{reminder.id}",
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 204

    # Verify soft delete (is_active=False)
    await test_db.refresh(reminder)
    assert reminder.is_active is False


@pytest.mark.asyncio
async def test_delete_reminder_not_found(
    client: AsyncClient,
    test_session_id: str
):
    """Test deleting non-existent reminder returns 404"""
    response = await client.delete(
        "/api/reminders/99999",
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_reminder_wrong_user(
    client: AsyncClient,
    test_db,
    test_session_id: str
):
    """Test user cannot delete another user's reminder"""
    # Create another user
    other_user = User(
        chat_id=987654321,
        latitude=40.0,
        longitude=-74.0,
        timezone="America/New_York"
    )
    test_db.add(other_user)
    await test_db.commit()
    await test_db.refresh(other_user)

    # Create reminder for other user
    reminder = Reminder(
        user_id=other_user.id,
        condition="rain",
        hours_ahead=6,
        is_active=True
    )
    test_db.add(reminder)
    await test_db.commit()
    await test_db.refresh(reminder)

    # Try to delete with current user's session
    response = await client.delete(
        f"/api/reminders/{reminder.id}",
        headers={"X-Session-ID": test_session_id}
    )

    assert response.status_code == 404  # Not found (ownership check)

    # Verify reminder is still active
    await test_db.refresh(reminder)
    assert reminder.is_active is True
