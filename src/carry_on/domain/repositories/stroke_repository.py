"""StrokeRepository protocol defining the repository interface."""

from typing import Protocol, runtime_checkable

from carry_on.domain.entities.stroke import Stroke, StrokeId


@runtime_checkable
class StrokeRepository(Protocol):
    """Repository interface for Stroke entities.

    Defines the contract for stroke persistence operations.
    Implementations handle the actual storage mechanism (MongoDB, etc.).

    Note: user_id is passed as a parameter rather than stored in the entity
    because user ownership is a query/security concern, not part of the
    domain concept of a stroke.
    """

    def save(self, stroke: Stroke, user_id: str) -> StrokeId:
        """Save a stroke and return its ID.

        Args:
            stroke: The stroke entity to save.
            user_id: The ID of the user who owns this stroke.

        Returns:
            The StrokeId of the saved stroke.
        """

    def find_by_user(self, user_id: str, limit: int = 20) -> list[Stroke]:
        """Find strokes for a user, newest first.

        Args:
            user_id: The ID of the user whose strokes to find.
            limit: Maximum number of strokes to return (default 20).

        Returns:
            List of Stroke entities, ordered by creation time descending.
        """
