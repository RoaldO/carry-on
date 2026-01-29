"""Tests for MongoUserRepository."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock

import allure
from bson import ObjectId
from pymongo.collection import Collection
import pytest

from carry_on.domain.entities.user import User, UserId
from carry_on.domain.repositories.user_repository import UserRepository
from carry_on.infrastructure.repositories.mongo_user_repository import (
    MongoUserRepository,
)


@pytest.fixture
def user_collection() -> MagicMock:
    return MagicMock(spec=Collection)


@pytest.fixture
def user_repo(user_collection: MagicMock) -> UserRepository:
    return MongoUserRepository(user_collection)


@allure.feature("Infrastructure")
@allure.story("MongoDB User Repository")
class TestUserRepositoryProtocol:
    """Tests for UserRepository protocol compliance."""

    def test_mongo_repository_implements_protocol(
        self,
        user_repo: UserRepository,
    ) -> None:
        """MongoUserRepository should implement UserRepository protocol."""
        assert isinstance(user_repo, UserRepository)


@allure.feature("Infrastructure")
@allure.story("MongoDB User Repository")
class TestMongoUserRepositorySave:
    """Tests for MongoUserRepository.save() method."""

    def test_save_new_user_returns_user_id(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should return UserId with inserted document ID for new users."""
        inserted_id = ObjectId()
        user_collection.insert_one.return_value = Mock(inserted_id=inserted_id)

        user = User.create_pending(email="test@example.com", display_name="Test User")

        result = user_repo.save(user)

        assert isinstance(result, UserId)
        assert result.value == str(inserted_id)

    def test_save_new_user_creates_correct_document(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should create MongoDB document with correct structure."""
        user_collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        user = User.create_pending(email="Test@Example.com", display_name="Test User")

        user_repo.save(user)

        user_collection.insert_one.assert_called_once()
        doc = user_collection.insert_one.call_args[0][0]

        assert doc["email"] == "test@example.com"  # lowercased
        assert doc["display_name"] == "Test User"
        assert doc["pin_hash"] is None
        assert doc["activated_at"] is None

    def test_save_activated_user_includes_pin_hash_and_timestamp(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should save activated user with PIN hash and activation timestamp."""
        user_collection.insert_one.return_value = Mock(inserted_id=ObjectId())

        activated_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        user = User(
            email="test@example.com",
            display_name="Test User",
            pin_hash="hashed_pin_123",
            activated_at=activated_at,
        )

        user_repo.save(user)

        doc = user_collection.insert_one.call_args[0][0]
        assert doc["pin_hash"] == "hashed_pin_123"
        assert doc["activated_at"] == "2024-01-15T10:00:00+00:00"

    def test_save_existing_user_updates_document(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should update existing user instead of inserting."""
        user_id = ObjectId()
        user = User(
            id=UserId(value=str(user_id)),
            email="test@example.com",
            display_name="Updated Name",
            pin_hash="new_hash",
            activated_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
        )

        result = user_repo.save(user)

        user_collection.update_one.assert_called_once()
        assert user_collection.insert_one.call_count == 0
        assert result == user.id


@allure.feature("Infrastructure")
@allure.story("MongoDB User Repository")
class TestMongoUserRepositoryFindByEmail:
    """Tests for MongoUserRepository.find_by_email() method."""

    def test_find_by_email_returns_user(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should return User entity when found."""
        doc_id = ObjectId()
        user_collection.find_one.return_value = {
            "_id": doc_id,
            "email": "test@example.com",
            "display_name": "Test User",
            "pin_hash": "hashed_pin",
            "activated_at": "2024-01-15T10:00:00+00:00",
        }

        result = user_repo.find_by_email("test@example.com")

        assert result is not None
        assert isinstance(result, User)
        assert result.id == UserId(value=str(doc_id))
        assert result.email == "test@example.com"
        assert result.display_name == "Test User"
        assert result.pin_hash == "hashed_pin"
        assert result.activated_at == datetime(
            2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc
        )

    def test_find_by_email_returns_none_when_not_found(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should return None when user not found."""
        user_collection.find_one.return_value = None

        result = user_repo.find_by_email("nonexistent@example.com")

        assert result is None

    def test_find_by_email_is_case_insensitive(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should search with lowercase email."""
        user_collection.find_one.return_value = None

        user_repo.find_by_email("Test@Example.COM")

        user_collection.find_one.assert_called_once_with({"email": "test@example.com"})

    def test_find_by_email_handles_pending_user(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should correctly map pending (non-activated) users."""
        doc_id = ObjectId()
        user_collection.find_one.return_value = {
            "_id": doc_id,
            "email": "test@example.com",
            "display_name": "Test User",
            "pin_hash": None,
            "activated_at": None,
        }

        result = user_repo.find_by_email("test@example.com")

        assert result is not None
        assert result.is_activated is False
        assert result.pin_hash is None
        assert result.activated_at is None


@allure.feature("Infrastructure")
@allure.story("MongoDB User Repository")
class TestMongoUserRepositoryFindById:
    """Tests for MongoUserRepository.find_by_id() method."""

    def test_find_by_id_returns_user(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should return User entity when found."""
        doc_id = ObjectId()
        user_collection.find_one.return_value = {
            "_id": doc_id,
            "email": "test@example.com",
            "display_name": "Test User",
            "pin_hash": "hashed_pin",
            "activated_at": "2024-01-15T10:00:00+00:00",
        }

        result = user_repo.find_by_id(UserId(value=str(doc_id)))

        assert result is not None
        assert result.id == UserId(value=str(doc_id))

    def test_find_by_id_returns_none_when_not_found(
        self,
        user_collection: MagicMock,
        user_repo: UserRepository,
    ) -> None:
        """Should return None when user not found."""
        user_collection.find_one.return_value = None

        result = user_repo.find_by_id(UserId(value=str(ObjectId())))

        assert result is None
