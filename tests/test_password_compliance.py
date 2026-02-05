"""Tests for password complexity validation."""

import allure
import pytest
from pydantic import ValidationError

from carry_on.api.schema import ActivateRequest, LoginRequest
from carry_on.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher


@pytest.fixture
def hasher() -> Argon2PasswordHasher:
    """Create a password hasher for tests."""
    return Argon2PasswordHasher()


@allure.feature("Security")
@allure.story("Password Complexity")
class TestPasswordCompliance:
    """Tests for password complexity validation."""

    def test_password_too_short_rejected(self, hasher: Argon2PasswordHasher) -> None:
        """Passwords under 8 characters should be rejected."""
        assert hasher.is_compliant("1234567") is False

    def test_password_exactly_8_chars_accepted(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Passwords of exactly 8 characters should be accepted."""
        assert hasher.is_compliant("12345678") is True

    def test_password_longer_than_8_chars_accepted(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Passwords longer than 8 characters should be accepted."""
        assert hasher.is_compliant("123456789") is True

    def test_password_with_letters_accepted(self, hasher: Argon2PasswordHasher) -> None:
        """Passwords with letters should be accepted."""
        assert hasher.is_compliant("Abcd1234") is True

    def test_password_with_special_chars_accepted(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Passwords with special characters should be accepted."""
        assert hasher.is_compliant("MyP@ss12") is True

    def test_password_no_max_length(self, hasher: Argon2PasswordHasher) -> None:
        """Long passwords should be accepted (no max limit)."""
        long_password = "A" * 100 + "1b!"
        assert hasher.is_compliant(long_password) is True

    def test_empty_password_rejected(self, hasher: Argon2PasswordHasher) -> None:
        """Empty password should be rejected."""
        assert hasher.is_compliant("") is False

    def test_4_char_pin_rejected(self, hasher: Argon2PasswordHasher) -> None:
        """Old-style 4-char PIN should be rejected."""
        assert hasher.is_compliant("1234") is False


@allure.feature("Security")
@allure.story("Password Validation Models")
class TestActivateRequestValidation:
    """Tests for ActivateRequest password validation."""

    def test_rejects_password_under_8_chars(self) -> None:
        """ActivateRequest should reject passwords under 8 characters."""
        with pytest.raises(ValidationError):
            ActivateRequest(email="test@example.com", password="1234567")

    def test_accepts_password_of_8_chars(self) -> None:
        """ActivateRequest should accept 8 character password."""
        req = ActivateRequest(email="test@example.com", password="12345678")
        assert req.password == "12345678"

    def test_accepts_long_password(self) -> None:
        """ActivateRequest should accept very long passwords (no max)."""
        long_pw = "a" * 200
        req = ActivateRequest(email="test@example.com", password=long_pw)
        assert len(req.password) == 200

    def test_accepts_special_characters(self) -> None:
        """ActivateRequest should accept special characters in password."""
        req = ActivateRequest(email="test@example.com", password="P@ssw0rd!")
        assert req.password == "P@ssw0rd!"


@allure.feature("Security")
@allure.story("Password Validation Models")
class TestLoginRequestValidation:
    """Tests for LoginRequest password validation (allows legacy 4-char)."""

    def test_accepts_4_char_password_for_migration(self) -> None:
        """LoginRequest should accept 4-char passwords for migration support."""
        req = LoginRequest(email="test@example.com", password="1234")
        assert req.password == "1234"

    def test_rejects_password_under_4_chars(self) -> None:
        """LoginRequest should reject passwords under 4 characters."""
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com", password="123")

    def test_accepts_long_password(self) -> None:
        """LoginRequest should accept very long passwords (no max)."""
        long_pw = "a" * 200
        req = LoginRequest(email="test@example.com", password=long_pw)
        assert len(req.password) == 200

    def test_accepts_special_characters(self) -> None:
        """LoginRequest should accept special characters in password."""
        req = LoginRequest(email="test@example.com", password="P@ssw0rd!")
        assert req.password == "P@ssw0rd!"
