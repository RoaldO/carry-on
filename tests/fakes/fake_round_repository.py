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
        """Save a round and return its ID.

        Args:
            round: The round aggregate to save.
            user_id: The ID of the user who owns this round.

        Returns:
            The RoundId of the saved round.
        """
        round_id = RoundId(value=str(uuid4()))
        saved_round = Round.create(
            course=round.course,
            date=round.date,
            id=round_id,
        )
        for hole in round.holes:
            saved_round.record_hole(hole)
        self._rounds.append((saved_round, user_id))
        return round_id

    def find_by_user(self, user_id: str) -> list[Round]:
        """Find rounds for a user.

        Args:
            user_id: The ID of the user whose rounds to find.

        Returns:
            List of Round aggregates owned by the user.
        """
        return [round for round, uid in self._rounds if uid == user_id]

    def clear(self) -> None:
        """Clear all stored rounds. Useful for test setup/teardown."""
        self._rounds.clear()

    @property
    def rounds(self) -> list[tuple[Round, str]]:
        """Get all stored rounds with their user IDs for test assertions."""
        return list(self._rounds)
