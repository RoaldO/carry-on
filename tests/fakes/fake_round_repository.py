"""In-memory fake implementation of RoundRepository for testing."""

from uuid import uuid4

from carry_on.domain.course.aggregates.round import Round, RoundId


class FakeRoundRepository:
    """In-memory implementation of RoundRepository for testing.

    Stores rounds in memory and provides the same interface as the
    real MongoDB repository, enabling tests without database access.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._rounds: list[tuple[Round, str]] = []  # (round, user_id)

    def save(self, round: Round, user_id: str) -> RoundId:
        """Save a round (insert if new, update if existing).

        Args:
            round: The round aggregate to save.
            user_id: The ID of the user who owns this round.

        Returns:
            The RoundId of the saved round.
        """
        if round.id is None:
            # Insert new round
            round_id = RoundId(value=str(uuid4()))
            saved_round = Round.create(
                course_name=round.course_name,
                date=round.date,
                id=round_id,
                status=round.status,
                player_handicap=round.player_handicap,
                stableford_score=round.stableford_score,
                slope_rating=round.slope_rating,
                course_rating=round.course_rating,
                course_handicap=round.course_handicap,
                num_holes=round.num_holes,
                course_par=round.course_par,
            )
            for hole in round.holes:
                saved_round.record_hole(hole)
            self._rounds.append((saved_round, user_id))
            return round_id
        else:
            # Update existing round
            for i, (existing_round, uid) in enumerate(self._rounds):
                if existing_round.id == round.id and uid == user_id:
                    saved_round = Round.create(
                        course_name=round.course_name,
                        date=round.date,
                        id=round.id,
                        status=round.status,
                        player_handicap=round.player_handicap,
                        stableford_score=round.stableford_score,
                        slope_rating=round.slope_rating,
                        course_rating=round.course_rating,
                        course_handicap=round.course_handicap,
                        num_holes=round.num_holes,
                        course_par=round.course_par,
                    )
                    for hole in round.holes:
                        saved_round.record_hole(hole)
                    self._rounds[i] = (saved_round, user_id)
                    return round.id
            # If not found, treat as insert
            saved_round = Round.create(
                course_name=round.course_name,
                date=round.date,
                id=round.id,
                status=round.status,
                player_handicap=round.player_handicap,
                stableford_score=round.stableford_score,
                slope_rating=round.slope_rating,
                course_rating=round.course_rating,
                course_handicap=round.course_handicap,
                num_holes=round.num_holes,
                course_par=round.course_par,
            )
            for hole in round.holes:
                saved_round.record_hole(hole)
            self._rounds.append((saved_round, user_id))
            return round.id

    def find_by_user(self, user_id: str) -> list[Round]:
        """Find rounds for a user.

        Args:
            user_id: The ID of the user whose rounds to find.

        Returns:
            List of Round aggregates owned by the user.
        """
        return [round for round, uid in self._rounds if uid == user_id]

    def find_by_id(self, round_id: RoundId, user_id: str) -> Round | None:
        """Find a round by ID for a specific user.

        Args:
            round_id: The ID of the round to find.
            user_id: The ID of the user who owns the round.

        Returns:
            The Round aggregate if found, None otherwise.
        """
        for round, uid in self._rounds:
            if round.id == round_id and uid == user_id:
                return round
        return None

    def clear(self) -> None:
        """Clear all stored rounds. Useful for test setup/teardown."""
        self._rounds.clear()

    @property
    def rounds(self) -> list[tuple[Round, str]]:
        """Get all stored rounds with their user IDs for test assertions."""
        return list(self._rounds)
