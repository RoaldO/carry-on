"""Pytest fixtures for CarryOn API tests."""

from collections.abc import Generator
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from bson import ObjectId
from dependency_injector import providers
from fastapi.testclient import TestClient

from carry_on.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from carry_on.services.course_service import CourseService
from carry_on.services.stroke_service import StrokeService

from tests.fakes.fake_course_repository import FakeCourseRepository
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
def client() -> Iterator[TestClient]:
    """Create test client with container available for overrides."""
    from carry_on.api.index import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def override_stroke_repo(
    fake_stroke_service: StrokeService,
    client: TestClient,
) -> Generator[FakeStrokeRepository, None, None]:
    """Override stroke service with fake repository in DI container.

    Activates the override so requests through ``client`` use the fake.
    Yields the fake repository for test assertions.
    """
    from carry_on.api import container

    with container.stroke_service.override(providers.Object(fake_stroke_service)):
        yield fake_stroke_service._repository  # type: ignore[misc]


@pytest.fixture
def fake_course_repository() -> FakeCourseRepository:
    """Create a fresh fake course repository for each test."""
    return FakeCourseRepository()


@pytest.fixture
def fake_course_service(fake_course_repository: FakeCourseRepository) -> CourseService:
    """Create a CourseService with the fake repository."""
    return CourseService(fake_course_repository)


@pytest.fixture
def override_course_repo(
    fake_course_service: CourseService,
    client: TestClient,
) -> Generator[FakeCourseRepository, None, None]:
    """Override course service with fake repository in DI container.

    Activates the override so requests through ``client`` use the fake.
    Yields the fake repository for test assertions.
    """
    from carry_on.api import container

    with container.course_service.override(providers.Object(fake_course_service)):
        yield fake_course_service._repository  # type: ignore[misc]


@pytest.fixture
def fake_round_repository():  # type: ignore[no-untyped-def]
    """Create a fresh fake round repository for each test."""
    from tests.fakes.fake_round_repository import FakeRoundRepository

    return FakeRoundRepository()


@pytest.fixture
def fake_round_service(fake_round_repository):  # type: ignore[no-untyped-def]
    """Create a RoundService with the fake repository."""
    from carry_on.services.round_service import RoundService

    return RoundService(fake_round_repository)


@pytest.fixture
def override_round_repo(
    fake_round_service,  # type: ignore[no-untyped-def]
    client: TestClient,
) -> Generator:
    """Override round service with fake repository in DI container.

    Activates the override so requests through ``client`` use the fake.
    Yields the fake repository for test assertions.
    """
    from carry_on.api import container

    with container.round_service.override(providers.Object(fake_round_service)):
        yield fake_round_service._repository


@pytest.fixture
def auth_headers(test_email: str, test_password: str) -> dict[str, str]:
    """Headers with valid email and password for authenticated requests."""
    return {"X-Email": test_email, "X-Password": test_password}


@pytest.fixture
def mock_ideas_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB ideas collection via container override."""
    from carry_on.api import container

    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value.limit.return_value = []
    mock_collection.insert_one.return_value.inserted_id = "test_idea_123"

    with container.ideas_collection.override(providers.Object(mock_collection)):
        yield mock_collection


@pytest.fixture
def mock_users_collection() -> Generator[MagicMock, None, None]:
    """Mock MongoDB users collection via container override."""
    from carry_on.api import container

    mock_collection = MagicMock()
    mock_collection.find_one.return_value = None

    with container.users_collection.override(providers.Object(mock_collection)):
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
