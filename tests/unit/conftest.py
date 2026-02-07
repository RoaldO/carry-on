"""Pytest fixtures for CarryOn API tests."""

import os
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch
import warnings

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from carry_on.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from carry_on.services.stroke_service import StrokeService

from tests.fakes.fake_stroke_repository import FakeStrokeRepository

# Test password hasher instance
_test_hasher = Argon2PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password for test data setup."""
    return _test_hasher.hash(password)


# Valid ObjectId for test user
TEST_USER_ID = ObjectId("507f1f77bcf86cd799439011")


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
def fake_stroke_service(fake_stroke_repository: FakeStrokeRepository) -> StrokeService:
    """Create a StrokeService with the fake repository."""
    return StrokeService(fake_stroke_repository)


@pytest.fixture
def test_email() -> str:
    """Test email for authentication."""
    return "test@example.com"


@pytest.fixture
def test_password() -> str:
    """Test password for authentication."""
    return "1234"


@pytest.fixture
def test_password_hashed(test_password: str) -> str:
    """Test password hashed with Argon2 for authentication tests."""
    return hash_password(test_password)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create test client.

    DEPRECATED: Use client_with_fake_repo for proper DI.
    Kept for backward compatibility with existing tests.
    """
    warnings.warn("Use client_with_fake_repo instead for proper DI", DeprecationWarning)
    os.environ["MONGODB_URI"] = "mongodb://test"

    # Import app after setting env vars
    from carry_on.api.index import app

    with TestClient(app) as client:
        yield client

    # Cleanup
    os.environ.pop("MONGODB_URI", None)


@pytest.fixture
def client_with_fake_repo(
    fake_stroke_service: StrokeService,
) -> Generator[tuple[TestClient, FakeStrokeRepository], None, None]:
    """Create test client with fake repository injected via DI.

    Returns a tuple of (client, fake_repository) so tests can inspect
    the repository state after making requests.
    """
    os.environ["MONGODB_URI"] = "mongodb://test"

    from carry_on.api.index import app
    from carry_on.api.strokes import get_stroke_service

    # Override the dependency to use our fake service
    app.dependency_overrides[get_stroke_service] = lambda: fake_stroke_service

    with TestClient(app) as client:
        yield client, fake_stroke_service._repository  # type: ignore[misc]

    # Cleanup
    app.dependency_overrides.clear()
    os.environ.pop("MONGODB_URI", None)


@pytest.fixture
def auth_headers(test_email: str, test_password: str) -> dict[str, str]:
    """Headers with valid email and password for authenticated requests."""
    return {"X-Email": test_email, "X-Password": test_password}


@pytest.fixture
def mock_ideas_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB ideas collection."""
    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value.limit.return_value = []
    mock_collection.insert_one.return_value.inserted_id = "test_idea_123"

    with patch(
        "carry_on.services.idea_service.get_ideas_collection",
        return_value=mock_collection,
    ):
        yield mock_collection


@pytest.fixture
def mock_users_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB users collection for authentication service.

    DEPRECATED: Authentication now uses AuthenticationService.
    This fixture mocks get_users_collection at the service factory level.
    """
    warnings.warn("Use mock_authentication_service for proper DI", DeprecationWarning)
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None

    with patch(
        "carry_on.services.authentication_service.get_users_collection",
        return_value=mock_collection,
    ):
        yield mock_collection


@pytest.fixture
def mock_authenticated_user(
    mock_users_collection: MagicMock, test_email: str, test_password_hashed: str
) -> MagicMock:
    """Mock a valid authenticated user in the database with hashed password."""
    mock_users_collection.find_one.return_value = {
        "_id": TEST_USER_ID,
        "email": test_email,
        "display_name": "Test User",
        "password_hash": test_password_hashed,
        "activated_at": "2026-01-25T10:00:00Z",
    }
    return mock_users_collection


@pytest.fixture
def mock_authenticated_user_plain_password(
    mock_users_collection: MagicMock, test_email: str, test_password: str
) -> MagicMock:
    """Mock a user with plain text password (legacy, needs rehash)."""
    mock_users_collection.find_one.return_value = {
        "_id": TEST_USER_ID,
        "email": test_email,
        "display_name": "Test User",
        "password_hash": test_password,
        "activated_at": "2026-01-25T10:00:00Z",
    }
    return mock_users_collection
