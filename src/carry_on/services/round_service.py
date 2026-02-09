"""RoundService application service for round operations."""

import datetime

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository
from carry_on.domain.course.value_objects.hole_result import HoleResult


class RoundService:
    """Application service for round operations.

    Orchestrates round creation and retrieval, delegating
    persistence to the repository.
    """

    def __init__(self, repository: RoundRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The round repository for persistence operations.
        """
        self._repository = repository

    def create_round(
        self,
        user_id: str,
        course_name: str,
        date: str,
        holes: list[dict],
    ) -> RoundId:
        """Record a new golf round.

        Args:
            user_id: The user recording the round.
            course_name: Name of the course played.
            date: Date of the round (ISO format string).
            holes: List of hole result dicts with hole_number, strokes,
                par, stroke_index.

        Returns:
            The ID of the saved round.

        Raises:
            ValueError: If round data is invalid.
        """
        round = Round.create(
            course_name=course_name,
            date=datetime.date.fromisoformat(date),
        )

        for h in holes:
            round.record_hole(
                HoleResult(
                    hole_number=h["hole_number"],
                    strokes=h["strokes"],
                    par=h["par"],
                    stroke_index=h["stroke_index"],
                )
            )

        return self._repository.save(round, user_id)

    def get_user_rounds(self, user_id: str) -> list[Round]:
        """Get rounds for a user.

        Args:
            user_id: The user whose rounds to retrieve.

        Returns:
            List of rounds owned by the user.
        """
        return self._repository.find_by_user(user_id)
