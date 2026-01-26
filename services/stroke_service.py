"""StrokeService application service for stroke operations."""

from datetime import date

from domain.entities.stroke import Stroke, StrokeId
from domain.repositories.stroke_repository import StrokeRepository
from domain.value_objects.club_type import ClubType
from domain.value_objects.distance import Distance


class StrokeService:
    """Application service for stroke operations.

    Orchestrates stroke creation and retrieval, delegating
    persistence to the repository.
    """

    def __init__(self, repository: StrokeRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The stroke repository for persistence operations.
        """
        self._repository = repository

    def record_stroke(
        self,
        user_id: str,
        club: str,
        stroke_date: date,
        distance: int | None = None,
        fail: bool = False,
    ) -> StrokeId:
        """Record a new stroke.

        Args:
            user_id: The user recording the stroke.
            club: Club code (e.g., "i7", "d").
            stroke_date: Date of the stroke.
            distance: Distance in meters (required if not fail).
            fail: Whether the stroke was a failure.

        Returns:
            The ID of the saved stroke.

        Raises:
            ValueError: If club is invalid or distance missing for success.
        """
        club_type = ClubType(club)  # Raises ValueError if invalid

        if fail:
            stroke = Stroke.create_failed(
                club=club_type,
                stroke_date=stroke_date,
            )
        else:
            stroke = Stroke.create_successful(
                club=club_type,
                distance=Distance(meters=distance),  # type: ignore[arg-type]
                stroke_date=stroke_date,
            )

        return self._repository.save(stroke, user_id)

    def get_user_strokes(self, user_id: str, limit: int = 20) -> list[Stroke]:
        """Get strokes for a user.

        Args:
            user_id: The user whose strokes to retrieve.
            limit: Maximum number of strokes (default 20).

        Returns:
            List of strokes, newest first.
        """
        return self._repository.find_by_user(user_id, limit)
