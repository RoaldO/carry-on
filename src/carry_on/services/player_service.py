"""Application service for player operations."""

from decimal import Decimal

from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.repositories.player_repository import PlayerRepository
from carry_on.domain.player.value_objects.handicap import Handicap


class PlayerService:
    """Application service for player profile operations.

    Orchestrates player retrieval and handicap updates, delegating
    persistence to the repository.
    """

    def __init__(self, repository: PlayerRepository) -> None:
        """Initialize the service with a repository.

        Args:
            repository: The player repository for persistence operations.
        """
        self._repository = repository

    def get_player(self, user_id: str) -> Player | None:
        """Get a player by their user ID.

        Args:
            user_id: The authentication user's ID.

        Returns:
            The Player if found, None otherwise.
        """
        return self._repository.find_by_user_id(user_id)

    def update_handicap(self, user_id: str, handicap_value: str | None) -> PlayerId:
        """Update a player's handicap, creating the player if needed.

        Args:
            user_id: The authentication user's ID.
            handicap_value: The new handicap as a string (for Decimal
                precision), or None to clear.

        Returns:
            The PlayerId of the saved player.

        Raises:
            ValueError: If handicap_value is outside the valid WHS range.
        """
        handicap = (
            Handicap(value=Decimal(handicap_value))
            if handicap_value is not None
            else None
        )

        existing = self._repository.find_by_user_id(user_id)

        if existing is not None:
            player = existing.update_handicap(handicap)
        else:
            player = Player(id=None, user_id=user_id, handicap=handicap)

        return self._repository.save(player)
