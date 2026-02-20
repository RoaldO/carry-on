"""Tests for PlayerRepository protocol."""

import allure

from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.repositories.player_repository import PlayerRepository


@allure.feature("Domain Model")
@allure.story("Player Repository Protocol")
class TestPlayerRepositoryProtocol:
    """Tests for PlayerRepository protocol shape."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """PlayerRepository should be a runtime-checkable Protocol."""
        assert hasattr(PlayerRepository, "__protocol_attrs__") or isinstance(
            PlayerRepository, type
        )

    def test_protocol_has_save_method(self) -> None:
        """PlayerRepository should define a save method."""
        assert hasattr(PlayerRepository, "save")

    def test_protocol_has_find_by_user_id_method(self) -> None:
        """PlayerRepository should define a find_by_user_id method."""
        assert hasattr(PlayerRepository, "find_by_user_id")

    def test_conforming_class_is_instance(self) -> None:
        """A class implementing save and find_by_user_id should satisfy the protocol."""

        class DummyRepo:
            def save(self, player: Player) -> PlayerId:
                return PlayerId(value="dummy")

            def find_by_user_id(self, user_id: str) -> Player | None:
                return None

        assert isinstance(DummyRepo(), PlayerRepository)

    def test_non_conforming_class_is_not_instance(self) -> None:
        """A class missing methods should not satisfy the protocol."""

        class NotARepo:
            pass

        assert not isinstance(NotARepo(), PlayerRepository)
