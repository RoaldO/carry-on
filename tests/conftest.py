"""Pytest fixtures for CarryOn API tests."""

import os
from collections.abc import Generator
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock, patch
import warnings

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from carry_on.api.pin_security import hash_pin
from carry_on.services.stroke_service import StrokeService
from tests.fakes.fake_stroke_repository import FakeStrokeRepository


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    """Write warnings to a file after test session completes."""
    warnings_file = Path("warnings.txt")

    # Get warnings from pytest's warning summary
    warning_reports = terminalreporter.stats.get("warnings", [])

    if warning_reports:
        with warnings_file.open("w") as f:
            f.write(f"# Test Warnings ({len(warning_reports)} total)\n\n")
            for i, warning in enumerate(warning_reports, 1):
                f.write(f"## Warning {i}\n")
                f.write(f"```\n{warning.message}\n```\n\n")
    elif warnings_file.exists():
        warnings_file.unlink()


@pytest.fixture
def fake_stroke_repository() -> FakeStrokeRepository:
    """Create a fresh fake stroke repository for each test."""
    return FakeStrokeRepository()


@pytest.fixture
def fake_stroke_service(
    fake_stroke_repository: FakeStrokeRepository,
    app: FastAPI,
) -> Iterator[StrokeService]:
    """Create a StrokeService with the fake repository."""

    from carry_on.api.strokes import get_stroke_service

    fake_service = StrokeService(fake_stroke_repository)
    app.dependency_overrides[get_stroke_service] = lambda: fake_service
    yield fake_service
    app.dependency_overrides.clear()


@pytest.fixture
def mock_strokes_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB strokes collection.

    DEPRECATED: Use fake_stroke_repository instead for proper DI.
    Kept for backward compatibility with existing tests.
    """
    warnings.warn(
        "Use fake_stroke_repository instead for proper DI", DeprecationWarning
    )
    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value.limit.return_value = []
    mock_collection.insert_one.return_value.inserted_id = "test_id_123"

    with patch(
        "carry_on.api.strokes.get_strokes_collection", return_value=mock_collection
    ):
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
def mongodb_uri() -> Iterator[str]:
    uri = "mongodb://test"
    os.environ["MONGODB_URI"] = uri

    yield uri

    os.environ.pop("MONGODB_URI", None)


@pytest.fixture
def app(mongodb_uri: str) -> FastAPI:
    import carry_on.api.index

    return carry_on.api.index.app


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def register_fake_stroke_service(
    fake_stroke_service: StrokeService,
    app: FastAPI,
):
    from carry_on.api.strokes import get_stroke_service

    app.dependency_overrides[get_stroke_service] = lambda: fake_stroke_service
    yield
    app.dependency_overrides.clear()


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

    with patch("carry_on.api.ideas.get_ideas_collection", return_value=mock_collection):
        yield mock_collection


@pytest.fixture
def mock_users_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB users collection."""
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None

    with patch("carry_on.api.index.get_users_collection", return_value=mock_collection):
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
