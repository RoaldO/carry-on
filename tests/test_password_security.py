"""Tests for password security module."""

import allure

from carry_on.api.password_security import hash_password, needs_rehash, verify_password


@allure.feature("Security")
@allure.story("Password Hashing")
class TestHashPassword:
    """Tests for hash_password function."""

    def test_produces_argon2_format(self):
        """Hash should produce Argon2id format."""
        password = "1234"
        hashed = hash_password(password)
        assert hashed.startswith("$argon2id$")

    def test_different_hashes_for_same_password(self):
        """Same password should produce different hashes (due to random salt)."""
        password = "1234"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_hash_contains_parameters(self):
        """Hash should contain algorithm parameters."""
        hashed = hash_password("1234")
        # Argon2 PHC format: $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
        assert "$v=" in hashed
        assert "$m=" in hashed


@allure.feature("Security")
@allure.story("Password Verification")
class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_verify_with_argon2_hash(self):
        """Should verify password against Argon2 hash."""
        password = "1234"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password_against_argon2(self):
        """Should reject wrong password against Argon2 hash."""
        hashed = hash_password("1234")
        assert verify_password("9999", hashed) is False

    def test_verify_with_plain_text_legacy(self):
        """Should verify password against plain text (legacy format)."""
        plain_password = "1234"
        assert verify_password("1234", plain_password) is True

    def test_verify_wrong_password_against_plain_text(self):
        """Should reject wrong password against plain text."""
        plain_password = "1234"
        assert verify_password("9999", plain_password) is False

    def test_verify_empty_stored_hash(self):
        """Should reject password when stored hash is empty."""
        assert verify_password("1234", "") is False

    def test_verify_handles_invalid_argon2_hash(self):
        """Should handle malformed Argon2 hash gracefully."""
        # Starts with $argon2 but is invalid
        invalid_hash = "$argon2id$invalid"
        assert verify_password("1234", invalid_hash) is False


@allure.feature("Security")
@allure.story("Password Rehashing")
class TestNeedsRehash:
    """Tests for needs_rehash function."""

    def test_plain_text_needs_rehash(self):
        """Plain text password should need rehashing."""
        assert needs_rehash("1234") is True

    def test_current_argon2_no_rehash(self):
        """Current Argon2 hash should not need rehashing."""
        hashed = hash_password("1234")
        assert needs_rehash(hashed) is False

    def test_empty_string_needs_rehash(self):
        """Empty string should need rehashing."""
        assert needs_rehash("") is True

    def test_legacy_prefix_needs_rehash(self):
        """Non-Argon2 prefix should need rehashing."""
        assert needs_rehash("plain_password_5678") is True
