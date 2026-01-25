"""Pytest fixtures for CarryOn API tests."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.pin_security import hash_pin


@pytest.fixture
def mock_strokes_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB strokes collection."""
    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value.limit.return_value = []
    mock_collection.insert_one.return_value.inserted_id = "test_id_123"

    with patch("api.index.get_strokes_collection", return_value=mock_collection):
        yield mock_collection


@pytest.fixture
def test_email() -> str:
    """Test email for authentication."""
    return "test@example.com"


@pytest.fixture
def test_pin() -> str:
    """Test PIN for authentication."""
    return "1234"


@pytest.fixture
def test_pin_hashed(test_pin: str) -> str:
    """Test PIN hashed with Argon2 for authentication tests."""
    return hash_pin(test_pin)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    os.environ["MONGODB_URI"] = "mongodb://test"

    # Import app after setting env vars
    from api.index import app

    with TestClient(app) as client:
        yield client

    # Cleanup
    os.environ.pop("MONGODB_URI", None)


@pytest.fixture
def auth_headers(test_email: str, test_pin: str) -> dict[str, str]:
    """Headers with valid email and PIN for authenticated requests."""
    return {"X-Email": test_email, "X-Pin": test_pin}


@pytest.fixture
def mock_ideas_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB ideas collection."""
    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value.limit.return_value = []
    mock_collection.insert_one.return_value.inserted_id = "test_idea_123"

    with patch("api.index.get_ideas_collection", return_value=mock_collection):
        yield mock_collection


@pytest.fixture
def mock_users_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB users collection."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None

    with patch("api.index.get_users_collection", return_value=mock_collection):
        yield mock_collection


@pytest.fixture
def mock_authenticated_user(
    mock_users_collection: MagicMock, test_email: str, test_pin_hashed: str
) -> MagicMock:
    """Mock a valid authenticated user in the database with hashed PIN."""
    mock_users_collection.find_one.return_value = {
        "_id": "user123",
        "email": test_email,
        "display_name": "Test User",
        "pin_hash": test_pin_hashed,
        "activated_at": "2026-01-25T10:00:00Z",
    }
    return mock_users_collection


@pytest.fixture
def mock_authenticated_user_plain_pin(
    mock_users_collection: MagicMock, test_email: str, test_pin: str
) -> MagicMock:
    """Mock a user with plain text PIN (legacy, needs rehash)."""
    mock_users_collection.find_one.return_value = {
        "_id": "user123",
        "email": test_email,
        "display_name": "Test User",
        "pin_hash": test_pin,
        "activated_at": "2026-01-25T10:00:00Z",
    }
    return mock_users_collection
