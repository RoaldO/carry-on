"""Tests for password complexity validation."""

import pytest
import allure

from carry_on.api.pin_security import is_password_compliant


@allure.feature("Security")
@allure.story("Password Complexity")
class TestPasswordCompliance:
    """Tests for password complexity validation."""

    def test_password_too_short_rejected(self):
        """Passwords under 8 characters should be rejected."""
        assert is_password_compliant("1234567") is False

    def test_password_exactly_8_chars_accepted(self):
        """Passwords of exactly 8 characters should be accepted."""
        assert is_password_compliant("12345678") is True

    def test_password_longer_than_8_chars_accepted(self):
        """Passwords longer than 8 characters should be accepted."""
        assert is_password_compliant("123456789") is True

    def test_password_with_letters_accepted(self):
        """Passwords with letters should be accepted."""
        assert is_password_compliant("Abcd1234") is True

    def test_password_with_special_chars_accepted(self):
        """Passwords with special characters should be accepted."""
        assert is_password_compliant("MyP@ss12") is True

    def test_password_no_max_length(self):
        """Long passwords should be accepted (no max limit)."""
        long_password = "A" * 100 + "1b!"
        assert is_password_compliant(long_password) is True

    def test_empty_password_rejected(self):
        """Empty password should be rejected."""
        assert is_password_compliant("") is False

    def test_4_char_pin_rejected(self):
        """Old-style 4-char PIN should be rejected."""
        assert is_password_compliant("1234") is False
