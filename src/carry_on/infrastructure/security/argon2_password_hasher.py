"""Argon2 implementation of PasswordHasher protocol."""

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from carry_on.domain.security.password_hasher import MIN_PASSWORD_LENGTH


class Argon2PasswordHasher:
    """Argon2-based password hashing implementation.

    Uses Argon2id for secure password hashing. Supports verification
    of legacy plain text passwords for migration purposes.
    """

    def __init__(self) -> None:
        """Initialize with default Argon2 hasher."""
        self._hasher = Argon2Hasher()

    def hash(self, password: str) -> str:
        """Hash a password using Argon2id.

        Args:
            password: The plain text password to hash.

        Returns:
            The Argon2id hashed password string.
        """
        return self._hasher.hash(password)

    def verify(self, password: str, hash: str) -> bool:
        """Verify a password against a stored hash.

        Supports both Argon2 hashes and legacy plain text passwords.

        Args:
            password: The plain text password to verify.
            hash: The stored hash to verify against.

        Returns:
            True if the password matches, False otherwise.
        """
        if hash.startswith("$argon2"):
            try:
                self._hasher.verify(hash, password)
                return True
            except (VerifyMismatchError, InvalidHashError, VerificationError):
                return False
        else:
            # Plain text comparison (legacy)
            return hash == password

    def needs_rehash(self, hash: str) -> bool:
        """Check if a hash needs to be upgraded.

        Returns True for plain text passwords or Argon2 hashes
        with outdated parameters.

        Args:
            hash: The stored hash to check.

        Returns:
            True if the hash should be updated, False otherwise.
        """
        if not hash.startswith("$argon2"):
            return True  # Plain text needs hashing
        return self._hasher.check_needs_rehash(hash)

    def is_compliant(self, password: str) -> bool:
        """Check if a password meets complexity requirements.

        Requirements:
        - Minimum 8 characters
        - No maximum length
        - Any characters allowed

        Args:
            password: The plain text password to check.

        Returns:
            True if the password meets requirements, False otherwise.
        """
        return len(password) >= MIN_PASSWORD_LENGTH
