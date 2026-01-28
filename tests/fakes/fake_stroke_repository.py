"""In-memory fake implementation of StrokeRepository for testing."""

from datetime import UTC, datetime
from uuid import uuid4

from carry_on.domain.entities.stroke import Stroke, StrokeId
from carry_on.domain.repositories.stroke_repository import StrokeRepository


class FakeStrokeRepository(StrokeRepository):
    """In-memory implementation of StrokeRepository for testing.

    Stores strokes in memory and provides the same interface as the
    real MongoDB repository, enabling tests without database access.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._strokes: list[
            tuple[Stroke, str, datetime]
        ] = []  # (stroke, user_id, created_at)

    def save(self, stroke: Stroke, user_id: str) -> StrokeId:
        """Save a stroke and return its ID.

        Args:
            stroke: The stroke entity to save.
            user_id: The ID of the user who owns this stroke.

        Returns:
            The StrokeId of the saved stroke.
        """
        stroke_id = StrokeId(value=str(uuid4()))
        created_at = datetime.now(UTC)

        # Create a new stroke with the ID and created_at set
        if stroke.fail:
            saved_stroke = Stroke.create_failed(
                id=stroke_id,
                club=stroke.club,
                stroke_date=stroke.stroke_date,
                created_at=created_at,
            )
        else:
            saved_stroke = Stroke.create_successful(
                id=stroke_id,
                club=stroke.club,
                distance=stroke.distance,  # type: ignore[arg-type]
                stroke_date=stroke.stroke_date,
                created_at=created_at,
            )

        self._strokes.append((saved_stroke, user_id, created_at))
        return stroke_id

    def find_by_user(self, user_id: str, limit: int = 20) -> list[Stroke]:
        """Find strokes for a user, newest first.

        Args:
            user_id: The ID of the user whose strokes to find.
            limit: Maximum number of strokes to return (default 20).

        Returns:
            List of Stroke entities, ordered by creation time descending.
        """
        user_strokes = [
            (stroke, created_at)
            for stroke, uid, created_at in self._strokes
            if uid == user_id
        ]
        # Sort by created_at descending (newest first)
        user_strokes.sort(key=lambda x: x[1], reverse=True)
        return [stroke for stroke, _ in user_strokes[:limit]]

    def clear(self) -> None:
        """Clear all stored strokes. Useful for test setup/teardown."""
        self._strokes.clear()

    @property
    def strokes(self) -> list[tuple[Stroke, str]]:
        """Get all stored strokes with their user IDs for test assertions."""
        return [(stroke, user_id) for stroke, user_id, _ in self._strokes]
