"""Repository protocol for User persistence."""

from typing import Protocol, runtime_checkable

from carry_on.domain.entities.user import User, UserId


@runtime_checkable
class UserRepository(Protocol):
    """Protocol defining user persistence operations.

    This protocol defines the contract for storing and retrieving users.
    Implementations handle the details of the underlying storage mechanism.
    """

    def save(self, user: User) -> UserId:
        """Save a user and return its ID.

        For new users (id=None), creates a new record.
        For existing users, updates the record.

        Args:
            user: The user entity to save.

        Returns:
            The UserId of the saved user.
        """

    def find_by_id(self, user_id: UserId) -> User | None:
        """Find a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User if found, None otherwise.
        """

    def find_by_email(self, email: str) -> User | None:
        """Find a user by their email address.

        Email lookup is case-insensitive.

        Args:
            email: The email address to search for.

        Returns:
            The User if found, None otherwise.
        """
