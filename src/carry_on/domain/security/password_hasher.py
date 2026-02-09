"""Protocol for password hashing operations."""

from typing import Protocol, runtime_checkable

# Business rule: minimum password length requirement
MIN_PASSWORD_LENGTH = 8


@runtime_checkable
class PasswordHasher(Protocol):
    """Protocol defining password hashing operations.

    This protocol abstracts the password hashing algorithm, allowing
    different implementations (Argon2, bcrypt, etc.) to be used.
    """

    def hash(self, password: str) -> str:
        """Hash a password using the current algorithm.

        Args:
            password: The plain text password to hash.

        Returns:
            The hashed password string.
        """

    def verify(self, password: str, hash: str) -> bool:
        """Verify a password against a stored hash.

        Args:
            password: The plain text password to verify.
            hash: The stored hash to verify against.

        Returns:
            True if the password matches, False otherwise.
        """

    def needs_rehash(self, hash: str) -> bool:
        """Check if a hash needs to be upgraded.

        This may return True for:
        - Plain text passwords (legacy)
        - Hashes using outdated algorithm parameters
        - Hashes using a different algorithm

        Args:
            hash: The stored hash to check.

        Returns:
            True if the hash should be updated, False otherwise.
        """

    def is_compliant(self, password: str) -> bool:
        """Check if a password meets complexity requirements.

        Args:
            password: The plain text password to check.

        Returns:
            True if the password meets requirements, False otherwise.
        """
