"""Tests for User entity."""

from datetime import datetime, timezone

import allure
import pytest

from carry_on.domain.entities.user import User, UserId


@allure.feature("Domain")
@allure.story("User Entity")
class TestUserId:
    """Tests for UserId value object."""

    def test_user_id_is_frozen(self) -> None:
        """UserId should be immutable."""
        user_id = UserId(value="123")
        with pytest.raises(AttributeError):
            user_id.value = "456"  # type: ignore[misc]

    def test_user_id_equality(self) -> None:
        """UserId with same value should be equal."""
        id1 = UserId(value="123")
        id2 = UserId(value="123")
        assert id1 == id2

    def test_user_id_inequality(self) -> None:
        """UserId with different value should not be equal."""
        id1 = UserId(value="123")
        id2 = UserId(value="456")
        assert id1 != id2


@allure.feature("Domain")
@allure.story("User Entity")
class TestUserCreation:
    """Tests for User entity creation."""

    def test_create_pending_user(self) -> None:
        """Should create a pending user without password."""
        user = User.create_pending(email="test@example.com", display_name="Test User")

        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.pin_hash is None
        assert user.activated_at is None
        assert user.id is None

    def test_create_pending_lowercases_email(self) -> None:
        """Should lowercase email on creation."""
        user = User.create_pending(email="Test@Example.COM")

        assert user.email == "test@example.com"

    def test_create_user_requires_email(self) -> None:
        """Should raise ValueError if email is empty."""
        with pytest.raises(ValueError, match="Email is required"):
            User(email="", display_name="Test")

    def test_activated_user_requires_password_hash(self) -> None:
        """Should raise ValueError if activated without password hash."""
        with pytest.raises(
            ValueError, match="Activated users must have a password hash"
        ):
            User(
                email="test@example.com",
                display_name="Test",
                activated_at=datetime.now(timezone.utc),
                pin_hash=None,
            )


@allure.feature("Domain")
@allure.story("User Entity")
class TestUserActivation:
    """Tests for User activation."""

    def test_is_activated_false_for_pending_user(self) -> None:
        """Pending user should not be activated."""
        user = User.create_pending(email="test@example.com")

        assert user.is_activated is False

    def test_is_activated_true_for_activated_user(self) -> None:
        """User with activated_at should be activated."""
        user = User(
            email="test@example.com",
            display_name="Test",
            pin_hash="hash123",
            activated_at=datetime.now(timezone.utc),
        )

        assert user.is_activated is True

    def test_activate_pending_user(self) -> None:
        """Should activate a pending user."""
        user = User.create_pending(email="test@example.com", display_name="Test")
        activated_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        activated = user.activate(pin_hash="hash123", activated_at=activated_at)

        assert activated.is_activated is True
        assert activated.pin_hash == "hash123"
        assert activated.activated_at == activated_at
        assert activated.email == user.email
        assert activated.display_name == user.display_name

    def test_activate_already_activated_raises_error(self) -> None:
        """Should raise ValueError when activating already activated user."""
        user = User(
            email="test@example.com",
            display_name="Test",
            pin_hash="hash123",
            activated_at=datetime.now(timezone.utc),
        )

        with pytest.raises(ValueError, match="already activated"):
            user.activate(pin_hash="newhash", activated_at=datetime.now(timezone.utc))


@allure.feature("Domain")
@allure.story("User Entity")
class TestUserPasswordUpdate:
    """Tests for User password hash update."""

    def test_update_pin_hash(self) -> None:
        """Should update password hash preserving other fields."""
        user = User(
            id=UserId(value="123"),
            email="test@example.com",
            display_name="Test",
            pin_hash="old_hash",
            activated_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
        )

        updated = user.update_pin_hash("new_hash")

        assert updated.pin_hash == "new_hash"
        assert updated.id == user.id
        assert updated.email == user.email
        assert updated.display_name == user.display_name
        assert updated.activated_at == user.activated_at
