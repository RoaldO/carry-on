"""RoundService application service for round operations."""

import datetime
from decimal import Decimal

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.player.repositories.player_repository import PlayerRepository


class RoundService:
    """Application service for round operations.

    Orchestrates round creation and retrieval, delegating
    persistence to the repository.
    """

    def __init__(
        self,
        repository: RoundRepository,
        player_repository: PlayerRepository,
    ) -> None:
        """Initialize the service with repositories.

        Args:
            repository: The round repository for persistence operations.
            player_repository: The player repository to look up handicaps.
        """
        self._repository = repository
        self._player_repository = player_repository

    def create_round(
        self,
        user_id: str,
        course_name: str,
        date: str,
        holes: list[dict] | None = None,
        slope_rating: Decimal | None = None,
        course_rating: Decimal | None = None,
        num_holes: int | None = None,
        course_par: int | None = None,
    ) -> RoundId:
        """Record a new golf round (partial or complete).

        Args:
            user_id: The user recording the round.
            course_name: Name of the course played.
            date: Date of the round (ISO format string).
            holes: Optional list of hole result dicts with hole_number, strokes,
                par, stroke_index. Defaults to empty list for incremental workflow.

        Returns:
            The ID of the saved round.

        Raises:
            ValueError: If round data is invalid.
        """
        player = self._player_repository.find_by_user_id(user_id)
        player_handicap = (
            player.handicap.value
            if player is not None and player.handicap is not None
            else None
        )

        round = Round.create(
            course_name=course_name,
            date=datetime.date.fromisoformat(date),
            player_handicap=player_handicap,
            slope_rating=slope_rating,
            course_rating=course_rating,
            num_holes=num_holes,
            course_par=course_par,
        )

        if holes:
            for h in holes:
                round.record_hole(
                    HoleResult(
                        hole_number=h["hole_number"],
                        strokes=h["strokes"],
                        par=h["par"],
                        stroke_index=h["stroke_index"],
                        clubs_used=h.get("clubs_used"),
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

    def update_hole(
        self,
        user_id: str,
        round_id: RoundId,
        hole: dict,
    ) -> None:
        """Update a single hole in an existing round.

        Args:
            user_id: The user who owns the round.
            round_id: The ID of the round to update.
            hole: Hole result dict with hole_number, strokes, par, stroke_index.

        Raises:
            ValueError: If round doesn't exist.
        """
        round = self._repository.find_by_id(round_id, user_id)
        if round is None:
            raise ValueError(f"Round {round_id.value} not found")

        hole_result = HoleResult(**hole)

        # Update if exists, record if new
        if any(h.hole_number == hole_result.hole_number for h in round.holes):
            round.update_hole(hole_result)
        else:
            round.record_hole(hole_result)

        self._repository.save(round, user_id)

    def get_round(self, user_id: str, round_id: RoundId) -> Round | None:
        """Get a round by ID.

        Args:
            user_id: The user who owns the round.
            round_id: The ID of the round to retrieve.

        Returns:
            The Round aggregate if found, None otherwise.
        """
        return self._repository.find_by_id(round_id, user_id)

    def update_round_status(
        self,
        user_id: str,
        round_id: RoundId,
        action: str,
    ) -> None:
        """Update the status of a round.

        Args:
            user_id: The user who owns the round.
            round_id: The ID of the round to update.
            action: Status action to perform: "finish", "abort", or "resume".

        Raises:
            ValueError: If round doesn't exist or action is invalid.
        """
        round = self._repository.find_by_id(round_id, user_id)
        if round is None:
            raise ValueError(f"Round {round_id.value} not found")

        if action == "finish":
            round.finish()
        elif action == "abort":
            round.abort()
        elif action == "resume":
            round.resume()
        else:
            raise ValueError(f"Invalid action: {action}")

        self._repository.save(round, user_id)
