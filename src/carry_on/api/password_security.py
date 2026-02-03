"""Password hashing utilities with algorithm versioning."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from pydantic import BaseModel, Field

# Current preferred hasher
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using the current preferred algorithm (Argon2id)."""
    return _hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash (supports plain text and Argon2)."""
    if stored_hash.startswith("$argon2"):
        try:
            _hasher.verify(stored_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError, VerificationError):
            return False
    else:
        # Plain text comparison (legacy)
        return stored_hash == password


def needs_rehash(stored_hash: str) -> bool:
    """Check if hash needs to be upgraded (plain text or outdated params)."""
    if not stored_hash.startswith("$argon2"):
        return True  # Plain text needs hashing
    return _hasher.check_needs_rehash(stored_hash)


MIN_PASSWORD_LENGTH = 8


def is_password_compliant(password: str) -> bool:
    """Check if password meets complexity requirements.

    Requirements:
    - Minimum 8 characters
    - No maximum length
    - Any characters allowed (letters, numbers, special chars)
    """
    return len(password) >= MIN_PASSWORD_LENGTH


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user returned by verify_password()."""

    id: str
    email: str
    display_name: str


class EmailCheck(BaseModel):
    email: str = Field(..., min_length=1)


class ActivateRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    # min_length=4 allows legacy PINs for migration flow
    password: str = Field(..., min_length=4)
