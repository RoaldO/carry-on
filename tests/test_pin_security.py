"""Tests for PIN security module."""

import allure
import pytest

from api.pin_security import hash_pin, needs_rehash, verify_pin


@allure.feature("Security")
@allure.story("PIN Hashing")
class TestHashPin:
    """Tests for hash_pin function."""

    def test_produces_argon2_format(self):
        """Hash should produce Argon2id format."""
        pin = "1234"
        hashed = hash_pin(pin)
        assert hashed.startswith("$argon2id$")

    def test_different_hashes_for_same_pin(self):
        """Same PIN should produce different hashes (due to random salt)."""
        pin = "1234"
        hash1 = hash_pin(pin)
        hash2 = hash_pin(pin)
        assert hash1 != hash2

    def test_hash_contains_parameters(self):
        """Hash should contain algorithm parameters."""
        hashed = hash_pin("1234")
        # Argon2 PHC format: $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
        assert "$v=" in hashed
        assert "$m=" in hashed


@allure.feature("Security")
@allure.story("PIN Verification")
class TestVerifyPin:
    """Tests for verify_pin function."""

    def test_verify_with_argon2_hash(self):
        """Should verify PIN against Argon2 hash."""
        pin = "1234"
        hashed = hash_pin(pin)
        assert verify_pin(pin, hashed) is True

    def test_verify_wrong_pin_against_argon2(self):
        """Should reject wrong PIN against Argon2 hash."""
        hashed = hash_pin("1234")
        assert verify_pin("9999", hashed) is False

    def test_verify_with_plain_text_legacy(self):
        """Should verify PIN against plain text (legacy format)."""
        plain_pin = "1234"
        assert verify_pin("1234", plain_pin) is True

    def test_verify_wrong_pin_against_plain_text(self):
        """Should reject wrong PIN against plain text."""
        plain_pin = "1234"
        assert verify_pin("9999", plain_pin) is False

    def test_verify_empty_stored_hash(self):
        """Should reject PIN when stored hash is empty."""
        assert verify_pin("1234", "") is False

    def test_verify_handles_invalid_argon2_hash(self):
        """Should handle malformed Argon2 hash gracefully."""
        # Starts with $argon2 but is invalid
        invalid_hash = "$argon2id$invalid"
        assert verify_pin("1234", invalid_hash) is False


@allure.feature("Security")
@allure.story("PIN Rehashing")
class TestNeedsRehash:
    """Tests for needs_rehash function."""

    def test_plain_text_needs_rehash(self):
        """Plain text PIN should need rehashing."""
        assert needs_rehash("1234") is True

    def test_current_argon2_no_rehash(self):
        """Current Argon2 hash should not need rehashing."""
        hashed = hash_pin("1234")
        assert needs_rehash(hashed) is False

    def test_empty_string_needs_rehash(self):
        """Empty string should need rehashing."""
        assert needs_rehash("") is True

    def test_legacy_prefix_needs_rehash(self):
        """Non-Argon2 prefix should need rehashing."""
        assert needs_rehash("plain_pin_5678") is True
