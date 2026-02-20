"""Player entity representing a golfer's profile in the player bounded context."""

from dataclasses import dataclass
from typing import Self

from carry_on.domain.core.value_objects.identifier import Identifier
from carry_on.domain.player.value_objects.handicap import Handicap


class PlayerId(Identifier):
    __slots__ = ()


@dataclass
class Player:
    """Player entity holding a golfer's profile data.

    Unlike Stroke (where user_id is a query parameter), user_id is intrinsic
    to Player because of the 1:1 relationship between User and Player.

    Attributes:
        id: Unique identifier (None for unsaved players).
        user_id: The associated authentication user's ID.
        handicap: The golfer's WHS handicap index (None if not set).
    """

    id: PlayerId | None
    user_id: str
    handicap: Handicap | None = None

    def update_handicap(self, handicap: Handicap | None) -> Self:
        """Return a new Player with the given handicap.

        Args:
            handicap: The new handicap value, or None to clear.

        Returns:
            A new Player instance with the updated handicap.
        """
        return type(self)(
            id=self.id,
            user_id=self.user_id,
            handicap=handicap,
        )
