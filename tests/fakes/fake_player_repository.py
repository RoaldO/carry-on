"""In-memory fake implementation of PlayerRepository for testing."""

from uuid import uuid4

from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.repositories.player_repository import PlayerRepository


class FakePlayerRepository(PlayerRepository):
    """In-memory implementation of PlayerRepository for testing.

    Uses upsert semantics matching the real MongoPlayerRepository:
    one Player per user_id.
    """

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._players: dict[str, Player] = {}  # keyed by user_id

    def save(self, player: Player) -> PlayerId:
        """Save a player (upsert) and return its ID.

        Args:
            player: The player entity to save.

        Returns:
            The PlayerId of the saved player.
        """
        existing = self._players.get(player.user_id)
        if existing is not None and existing.id is not None:
            player_id = existing.id
        else:
            player_id = PlayerId(value=str(uuid4()))

        saved = Player(
            id=player_id,
            user_id=player.user_id,
            handicap=player.handicap,
        )
        self._players[player.user_id] = saved
        return player_id

    def find_by_user_id(self, user_id: str) -> Player | None:
        """Find a player by their associated user ID.

        Args:
            user_id: The authentication user's ID.

        Returns:
            The Player if found, None otherwise.
        """
        return self._players.get(user_id)

    def clear(self) -> None:
        """Clear all stored players. Useful for test setup/teardown."""
        self._players.clear()
