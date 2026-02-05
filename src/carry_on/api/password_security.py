"""Password security utilities and request models for authentication API."""

from pydantic import BaseModel, Field

from carry_on.infrastructure.security.argon2_password_hasher import (
    MIN_PASSWORD_LENGTH,
    Argon2PasswordHasher,
)

# Singleton hasher instance for backward compatibility
_hasher = Argon2PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using the current preferred algorithm (Argon2id).

    This function is kept for backward compatibility. New code should use
    the PasswordHasher protocol via dependency injection.
    """
    return _hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash (supports plain text and Argon2).

    This function is kept for backward compatibility. New code should use
    the PasswordHasher protocol via dependency injection.
    """
    return _hasher.verify(password, stored_hash)


def needs_rehash(stored_hash: str) -> bool:
    """Check if hash needs to be upgraded (plain text or outdated params).

    This function is kept for backward compatibility. New code should use
    the PasswordHasher protocol via dependency injection.
    """
    return _hasher.needs_rehash(stored_hash)


def is_password_compliant(password: str) -> bool:
    """Check if password meets complexity requirements.

    This function is kept for backward compatibility. New code should use
    the PasswordHasher protocol via dependency injection.
    """
    return _hasher.is_compliant(password)


class EmailCheck(BaseModel):
    """Request model for checking email existence."""

    email: str = Field(..., min_length=1)


class ActivateRequest(BaseModel):
    """Request model for account activation."""

    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)


class LoginRequest(BaseModel):
    """Request model for login."""

    email: str = Field(..., min_length=1)
    # min_length=4 allows legacy PINs for migration flow
    password: str = Field(..., min_length=4)


class UpdatePasswordRequest(BaseModel):
    """Request model for password update."""

    email: str = Field(..., min_length=1)
    current_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)
