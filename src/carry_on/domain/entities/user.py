"""User entity representing an application user."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class UserId:
    """Value object representing a unique user identifier."""

    value: str


@dataclass
class User:
    """Entity representing an application user.

    Users authenticate with email and password. New users must activate their
    account by setting a password before they can log in.
    """

    email: str
    display_name: str
    password_hash: str | None = None
    activated_at: datetime | None = None
    id: UserId | None = None

    def __post_init__(self) -> None:
        """Validate user state."""
        if not self.email:
            raise ValueError("Email is required")
        if self.activated_at and not self.password_hash:
            raise ValueError("Activated users must have a password hash")

    @property
    def is_activated(self) -> bool:
        """Check if user has completed activation."""
        return self.activated_at is not None

    @classmethod
    def create_pending(cls, email: str, display_name: str = "") -> "User":
        """Create a new user pending activation.

        Args:
            email: User's email address.
            display_name: User's display name (optional).

        Returns:
            New User instance awaiting activation.
        """
        return cls(email=email.lower(), display_name=display_name)

    def activate(self, password_hash: str, activated_at: datetime) -> "User":
        """Activate the user with a password.

        Args:
            password_hash: Hashed password for authentication.
            activated_at: Timestamp of activation.

        Returns:
            New User instance with activation complete.
        """
        if self.is_activated:
            raise ValueError("User is already activated")
        return User(
            id=self.id,
            email=self.email,
            display_name=self.display_name,
            password_hash=password_hash,
            activated_at=activated_at,
        )

    def update_password_hash(self, new_password_hash: str) -> "User":
        """Update the user's password hash (for rehashing).

        Args:
            new_password_hash: New hashed password.

        Returns:
            New User instance with updated password hash.
        """
        return User(
            id=self.id,
            email=self.email,
            display_name=self.display_name,
            password_hash=new_password_hash,
            activated_at=self.activated_at,
        )
