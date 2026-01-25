"""Pytest fixtures for CarryOn API tests."""

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_shots_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB shots collection."""
    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value.limit.return_value = []
    mock_collection.insert_one.return_value.inserted_id = "test_id_123"

    with patch("api.index.get_shots_collection", return_value=mock_collection):
        yield mock_collection


@pytest.fixture
def test_pin() -> str:
    """Test PIN for authentication."""
    return "1234"


@pytest.fixture
def client(test_pin: str) -> Generator[TestClient, None, None]:
    """Create test client with PIN configured."""
    os.environ["APP_PIN"] = test_pin
    os.environ["MONGODB_URI"] = "mongodb://test"

    # Import app after setting env vars
    from api.index import app

    with TestClient(app) as client:
        yield client

    # Cleanup
    os.environ.pop("APP_PIN", None)
    os.environ.pop("MONGODB_URI", None)


@pytest.fixture
def auth_headers(test_pin: str) -> dict[str, str]:
    """Headers with valid PIN for authenticated requests."""
    return {"X-Pin": test_pin}


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
