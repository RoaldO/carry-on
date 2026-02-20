"""Tests for PlayerService."""

from decimal import Decimal
from unittest.mock import MagicMock

import allure
import pytest

from carry_on.domain.player.entities.player import Player, PlayerId
from carry_on.domain.player.repositories.player_repository import PlayerRepository
from carry_on.domain.player.value_objects.handicap import Handicap
from carry_on.services.player_service import PlayerService


@allure.feature("Application Services")
@allure.story("Player Service")
class TestPlayerServiceInit:
    """Tests for PlayerService initialization."""

    def test_init_accepts_repository(self) -> None:
        """PlayerService should accept a repository in constructor."""
        repository = MagicMock(spec=PlayerRepository)
        service = PlayerService(repository)
        assert service._repository is repository


@allure.feature("Application Services")
@allure.story("Player Service")
class TestPlayerServiceGetPlayer:
    """Tests for PlayerService.get_player() method."""

    def test_get_player_delegates_to_repository(self) -> None:
        """Should delegate to repository with correct user_id."""
        repository = MagicMock(spec=PlayerRepository)
        expected_player = Player(
            id=PlayerId(value="p1"),
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )
        repository.find_by_user_id.return_value = expected_player
        service = PlayerService(repository)

        result = service.get_player("user123")

        assert result == expected_player
        repository.find_by_user_id.assert_called_once_with("user123")

    def test_get_player_returns_none_when_not_found(self) -> None:
        """Should return None when no player exists for user."""
        repository = MagicMock(spec=PlayerRepository)
        repository.find_by_user_id.return_value = None
        service = PlayerService(repository)

        result = service.get_player("nonexistent")

        assert result is None


@allure.feature("Application Services")
@allure.story("Player Service")
class TestPlayerServiceUpdateHandicap:
    """Tests for PlayerService.update_handicap() method."""

    def test_update_handicap_for_existing_player(self) -> None:
        """Should update existing player's handicap."""
        repository = MagicMock(spec=PlayerRepository)
        existing = Player(
            id=PlayerId(value="p1"),
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )
        repository.find_by_user_id.return_value = existing
        repository.save.return_value = PlayerId(value="p1")
        service = PlayerService(repository)

        service.update_handicap("user123", "18.5")

        repository.save.assert_called_once()
        saved_player = repository.save.call_args.args[0]
        assert saved_player.handicap == Handicap(value=Decimal("18.5"))
        assert saved_player.user_id == "user123"

    def test_update_handicap_for_new_player(self) -> None:
        """Should create new player when none exists."""
        repository = MagicMock(spec=PlayerRepository)
        repository.find_by_user_id.return_value = None
        repository.save.return_value = PlayerId(value="new_p")
        service = PlayerService(repository)

        service.update_handicap("user123", "14.3")

        repository.save.assert_called_once()
        saved_player = repository.save.call_args.args[0]
        assert saved_player.user_id == "user123"
        assert saved_player.handicap == Handicap(value=Decimal("14.3"))
        assert saved_player.id is None

    def test_update_handicap_to_none(self) -> None:
        """Should allow clearing handicap by passing None."""
        repository = MagicMock(spec=PlayerRepository)
        existing = Player(
            id=PlayerId(value="p1"),
            user_id="user123",
            handicap=Handicap(value=Decimal("14.3")),
        )
        repository.find_by_user_id.return_value = existing
        repository.save.return_value = PlayerId(value="p1")
        service = PlayerService(repository)

        service.update_handicap("user123", None)

        saved_player = repository.save.call_args.args[0]
        assert saved_player.handicap is None

    def test_update_handicap_invalid_value_raises_error(self) -> None:
        """Should raise ValueError for out-of-range handicap."""
        repository = MagicMock(spec=PlayerRepository)
        repository.find_by_user_id.return_value = None
        service = PlayerService(repository)

        with pytest.raises(ValueError, match="Handicap must be"):
            service.update_handicap("user123", "55.0")

        repository.save.assert_not_called()
