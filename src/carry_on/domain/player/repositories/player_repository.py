"""PlayerRepository protocol defining the repository interface."""

from typing import Protocol, runtime_checkable

from carry_on.domain.player.entities.player import Player, PlayerId


@runtime_checkable
class PlayerRepository(Protocol):
    """Repository interface for Player entities.

    Defines the contract for player persistence operations.
    Unlike StrokeRepository, user_id is stored inside the Player entity
    because it is intrinsic to the concept (1:1 with User).

    Implementations should use upsert semantics in save() since there
    is exactly one Player per User.
    """

    def save(self, player: Player) -> PlayerId:
        """Save a player (upsert) and return its ID.

        Args:
            player: The player entity to save.

        Returns:
            The PlayerId of the saved player.
        """

    def find_by_user_id(self, user_id: str) -> Player | None:
        """Find a player by their associated user ID.

        Args:
            user_id: The authentication user's ID.

        Returns:
            The Player if found, None otherwise.
        """
