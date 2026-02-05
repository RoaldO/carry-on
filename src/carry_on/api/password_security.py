"""Backward compatibility module for password security.

DEPRECATED: This module is kept for backward compatibility.
- For password hashing, use PasswordHasher protocol via dependency injection
- For request models, import from carry_on.api.schema
- For MIN_PASSWORD_LENGTH, import from carry_on.domain.security.password_hasher
"""

import warnings

from carry_on.api.schema import (
    ActivateRequest as ActivateRequest,
    EmailCheck as EmailCheck,
    LoginRequest as LoginRequest,
    UpdatePasswordRequest as UpdatePasswordRequest,
)
from carry_on.domain.security.password_hasher import (
    MIN_PASSWORD_LENGTH as MIN_PASSWORD_LENGTH,
)
from carry_on.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)

# Singleton hasher instance for backward compatibility
_hasher = Argon2PasswordHasher()


def _warn_deprecated(func_name: str) -> None:
    """Emit deprecation warning for function usage."""
    warnings.warn(
        f"{func_name}() is deprecated. Use PasswordHasher protocol via DI instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def hash_password(password: str) -> str:
    """Hash a password using the current preferred algorithm (Argon2id).

    DEPRECATED: Use PasswordHasher protocol via dependency injection.
    """
    _warn_deprecated("hash_password")
    return _hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash (supports plain text and Argon2).

    DEPRECATED: Use PasswordHasher protocol via dependency injection.
    """
    _warn_deprecated("verify_password")
    return _hasher.verify(password, stored_hash)


def needs_rehash(stored_hash: str) -> bool:
    """Check if hash needs to be upgraded (plain text or outdated params).

    DEPRECATED: Use PasswordHasher protocol via dependency injection.
    """
    _warn_deprecated("needs_rehash")
    return _hasher.needs_rehash(stored_hash)


def is_password_compliant(password: str) -> bool:
    """Check if password meets complexity requirements.

    DEPRECATED: Use PasswordHasher protocol via dependency injection.
    """
    _warn_deprecated("is_password_compliant")
    return _hasher.is_compliant(password)
