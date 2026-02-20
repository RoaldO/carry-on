"""Tests for Player entity."""

from decimal import Decimal

import allure

from carry_on.domain.core.value_objects.identifier import Identifier
from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.value_objects.handicap import Handicap


@allure.feature("Domain Model")
@allure.story("Player Entity")
class TestPlayerIdInheritance:
    """Tests for PlayerId type."""

    def test_player_id_inherits_from_identifier(self) -> None:
        """PlayerId should be a subclass of Identifier."""
        assert issubclass(PlayerId, Identifier)

    def test_player_id_creation(self) -> None:
        """Should create PlayerId with a string value."""
        pid = PlayerId(value="player123")
        assert pid.value == "player123"


@allure.feature("Domain Model")
@allure.story("Player Entity")
class TestPlayerCreation:
    """Tests for Player creation."""

    def test_create_player_with_handicap(self) -> None:
        """Should create Player with user_id and handicap."""
        handicap = Handicap(value=Decimal("14.3"))
        player = Player(id=None, user_id="user123", handicap=handicap)

        assert player.user_id == "user123"
        assert player.handicap == handicap
        assert player.id is None

    def test_create_player_without_handicap(self) -> None:
        """Should create Player with no handicap (None)."""
        player = Player(id=None, user_id="user123")

        assert player.user_id == "user123"
        assert player.handicap is None

    def test_create_player_with_id(self) -> None:
        """Should create Player with a provided ID."""
        pid = PlayerId(value="player456")
        player = Player(id=pid, user_id="user123")

        assert player.id == pid


@allure.feature("Domain Model")
@allure.story("Player Entity")
class TestPlayerUpdateHandicap:
    """Tests for Player.update_handicap() method."""

    def test_update_handicap_returns_new_player(self) -> None:
        """update_handicap should return a new Player, not mutate in place."""
        original = Player(id=PlayerId(value="p1"), user_id="user123")
        new_handicap = Handicap(value=Decimal("18.5"))

        updated = original.update_handicap(new_handicap)

        assert updated is not original
        assert updated.handicap == new_handicap
        assert original.handicap is None

    def test_update_handicap_preserves_id_and_user_id(self) -> None:
        """update_handicap should keep id and user_id unchanged."""
        pid = PlayerId(value="p1")
        original = Player(
            id=pid, user_id="user123", handicap=Handicap(value=Decimal("10.0"))
        )
        new_handicap = Handicap(value=Decimal("12.0"))

        updated = original.update_handicap(new_handicap)

        assert updated.id == pid
        assert updated.user_id == "user123"

    def test_update_handicap_to_none(self) -> None:
        """Should allow clearing the handicap by passing None."""
        original = Player(
            id=PlayerId(value="p1"),
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )

        updated = original.update_handicap(None)

        assert updated.handicap is None
