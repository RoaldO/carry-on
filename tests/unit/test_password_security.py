"""Tests for Argon2PasswordHasher."""

import allure
import pytest

from carry_on.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher


@pytest.fixture
def hasher() -> Argon2PasswordHasher:
    """Create a password hasher for tests."""
    return Argon2PasswordHasher()


@allure.feature("Security")
@allure.story("Password Hashing")
class TestHashPassword:
    """Tests for Argon2PasswordHasher.hash() method."""

    def test_produces_argon2_format(self, hasher: Argon2PasswordHasher) -> None:
        """Hash should produce Argon2id format."""
        password = "1234"
        hashed = hasher.hash(password)
        assert hashed.startswith("$argon2id$")

    def test_different_hashes_for_same_password(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Same password should produce different hashes (due to random salt)."""
        password = "1234"
        hash1 = hasher.hash(password)
        hash2 = hasher.hash(password)
        assert hash1 != hash2

    def test_hash_contains_parameters(self, hasher: Argon2PasswordHasher) -> None:
        """Hash should contain algorithm parameters."""
        hashed = hasher.hash("1234")
        # Argon2 PHC format: $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
        assert "$v=" in hashed
        assert "$m=" in hashed


@allure.feature("Security")
@allure.story("Password Verification")
class TestVerifyPassword:
    """Tests for Argon2PasswordHasher.verify() method."""

    def test_verify_with_argon2_hash(self, hasher: Argon2PasswordHasher) -> None:
        """Should verify password against Argon2 hash."""
        password = "1234"
        hashed = hasher.hash(password)
        assert hasher.verify(password, hashed) is True

    def test_verify_wrong_password_against_argon2(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Should reject wrong password against Argon2 hash."""
        hashed = hasher.hash("1234")
        assert hasher.verify("9999", hashed) is False

    def test_verify_with_plain_text_legacy(self, hasher: Argon2PasswordHasher) -> None:
        """Should verify password against plain text (legacy format)."""
        plain_password = "1234"
        assert hasher.verify("1234", plain_password) is True

    def test_verify_wrong_password_against_plain_text(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Should reject wrong password against plain text."""
        plain_password = "1234"
        assert hasher.verify("9999", plain_password) is False

    def test_verify_empty_stored_hash(self, hasher: Argon2PasswordHasher) -> None:
        """Should reject password when stored hash is empty."""
        assert hasher.verify("1234", "") is False

    def test_verify_handles_invalid_argon2_hash(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Should handle malformed Argon2 hash gracefully."""
        # Starts with $argon2 but is invalid
        invalid_hash = "$argon2id$invalid"
        assert hasher.verify("1234", invalid_hash) is False


@allure.feature("Security")
@allure.story("Password Rehashing")
class TestNeedsRehash:
    """Tests for Argon2PasswordHasher.needs_rehash() method."""

    def test_plain_text_needs_rehash(self, hasher: Argon2PasswordHasher) -> None:
        """Plain text password should need rehashing."""
        assert hasher.needs_rehash("1234") is True

    def test_current_argon2_no_rehash(self, hasher: Argon2PasswordHasher) -> None:
        """Current Argon2 hash should not need rehashing."""
        hashed = hasher.hash("1234")
        assert hasher.needs_rehash(hashed) is False

    def test_empty_string_needs_rehash(self, hasher: Argon2PasswordHasher) -> None:
        """Empty string should need rehashing."""
        assert hasher.needs_rehash("") is True

    def test_legacy_prefix_needs_rehash(self, hasher: Argon2PasswordHasher) -> None:
        """Non-Argon2 prefix should need rehashing."""
        assert hasher.needs_rehash("plain_password_5678") is True


@allure.feature("Security")
@allure.story("Password Compliance")
class TestIsCompliant:
    """Tests for Argon2PasswordHasher.is_compliant() method."""

    def test_short_password_not_compliant(self, hasher: Argon2PasswordHasher) -> None:
        """Password shorter than 8 chars should not be compliant."""
        assert hasher.is_compliant("1234567") is False

    def test_exactly_8_chars_is_compliant(self, hasher: Argon2PasswordHasher) -> None:
        """Password with exactly 8 chars should be compliant."""
        assert hasher.is_compliant("12345678") is True

    def test_long_password_is_compliant(self, hasher: Argon2PasswordHasher) -> None:
        """Long password should be compliant."""
        assert hasher.is_compliant("SecurePassword123!") is True
