"""RoundRepository protocol defining the repository interface."""

from typing import Protocol, runtime_checkable

from carry_on.domain.course.aggregates.round import Round, RoundId


@runtime_checkable
class RoundRepository(Protocol):
    """Repository interface for Round aggregates.

    Defines the contract for round persistence operations.
    Implementations handle the actual storage mechanism (MongoDB, etc.).
    """

    def save(self, round: Round, user_id: str) -> RoundId:
        """Save a round and return its ID.

        Args:
            round: The round aggregate to save.
            user_id: The ID of the user who owns this round.

        Returns:
            The RoundId of the saved round.
        """

    def find_by_user(self, user_id: str) -> list[Round]:
        """Find rounds for a user.

        Args:
            user_id: The ID of the user whose rounds to find.

        Returns:
            List of Round aggregates owned by the user.
        """

    def find_by_id(self, round_id: RoundId, user_id: str) -> Round | None:
        """Find a round by ID for a specific user.

        Args:
            round_id: The ID of the round to find.
            user_id: The ID of the user who owns the round.

        Returns:
            The Round aggregate if found, None otherwise.
        """
