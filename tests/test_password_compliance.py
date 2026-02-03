"""Tests for password complexity validation."""

import pytest
import allure
from pydantic import ValidationError

from carry_on.api import password_security


@allure.feature("Security")
@allure.story("Password Complexity")
class TestPasswordCompliance:
    """Tests for password complexity validation."""

    def test_password_too_short_rejected(self):
        """Passwords under 8 characters should be rejected."""
        assert password_security.is_password_compliant("1234567") is False

    def test_password_exactly_8_chars_accepted(self):
        """Passwords of exactly 8 characters should be accepted."""
        assert password_security.is_password_compliant("12345678") is True

    def test_password_longer_than_8_chars_accepted(self):
        """Passwords longer than 8 characters should be accepted."""
        assert password_security.is_password_compliant("123456789") is True

    def test_password_with_letters_accepted(self):
        """Passwords with letters should be accepted."""
        assert password_security.is_password_compliant("Abcd1234") is True

    def test_password_with_special_chars_accepted(self):
        """Passwords with special characters should be accepted."""
        assert password_security.is_password_compliant("MyP@ss12") is True

    def test_password_no_max_length(self):
        """Long passwords should be accepted (no max limit)."""
        long_password = "A" * 100 + "1b!"
        assert password_security.is_password_compliant(long_password) is True

    def test_empty_password_rejected(self):
        """Empty password should be rejected."""
        assert password_security.is_password_compliant("") is False

    def test_4_char_pin_rejected(self):
        """Old-style 4-char PIN should be rejected."""
        assert password_security.is_password_compliant("1234") is False


@allure.feature("Security")
@allure.story("Password Validation Models")
class TestActivateRequestValidation:
    """Tests for ActivateRequest password validation."""

    def test_rejects_password_under_8_chars(self):
        """ActivateRequest should reject passwords under 8 characters."""
        with pytest.raises(ValidationError):
            password_security.ActivateRequest(
                email="test@example.com", password="1234567"
            )

    def test_accepts_password_of_8_chars(self):
        """ActivateRequest should accept 8 character password."""
        req = password_security.ActivateRequest(
            email="test@example.com", password="12345678"
        )
        assert req.password == "12345678"

    def test_accepts_long_password(self):
        """ActivateRequest should accept very long passwords (no max)."""
        long_pw = "a" * 200
        req = password_security.ActivateRequest(
            email="test@example.com", password=long_pw
        )
        assert len(req.password) == 200

    def test_accepts_special_characters(self):
        """ActivateRequest should accept special characters in password."""
        req = password_security.ActivateRequest(
            email="test@example.com", password="P@ssw0rd!"
        )
        assert req.password == "P@ssw0rd!"


@allure.feature("Security")
@allure.story("Password Validation Models")
class TestLoginRequestValidation:
    """Tests for LoginRequest password validation (allows legacy 4-char)."""

    def test_accepts_4_char_password_for_migration(self):
        """LoginRequest should accept 4-char passwords for migration support."""
        req = password_security.LoginRequest(email="test@example.com", password="1234")
        assert req.password == "1234"

    def test_rejects_password_under_4_chars(self):
        """LoginRequest should reject passwords under 4 characters."""
        with pytest.raises(ValidationError):
            password_security.LoginRequest(email="test@example.com", password="123")

    def test_accepts_long_password(self):
        """LoginRequest should accept very long passwords (no max)."""
        long_pw = "a" * 200
        req = password_security.LoginRequest(email="test@example.com", password=long_pw)
        assert len(req.password) == 200

    def test_accepts_special_characters(self):
        """LoginRequest should accept special characters in password."""
        req = password_security.LoginRequest(
            email="test@example.com", password="P@ssw0rd!"
        )
        assert req.password == "P@ssw0rd!"
