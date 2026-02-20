"""Tests for Player API endpoints."""

from decimal import Decimal
from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from carry_on.domain.player.entities.player import Player
from carry_on.domain.player.value_objects.handicap import Handicap
from tests.fakes.fake_player_repository import FakePlayerRepository
from tests.unit.conftest import TEST_USER_ID


@allure.feature("REST API")
@allure.story("Player API")
class TestGetPlayerEndpoint:
    """Tests for GET /api/player/me endpoint."""

    def test_get_player_without_auth_returns_401(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """GET /api/player/me without authentication should return 401."""
        response = client.get("/api/player/me")
        assert response.status_code == 401

    def test_get_player_returns_handicap(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
        override_player_repo: FakePlayerRepository,
    ) -> None:
        """GET /api/player/me should return player handicap."""
        # Seed the fake repository with a player
        override_player_repo.save(
            Player(
                id=None,
                user_id=str(TEST_USER_ID),
                handicap=Handicap(value=Decimal("14.3")),
            )
        )

        response = client.get("/api/player/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["handicap"] == "14.3"

    def test_get_player_returns_null_when_no_player(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
        override_player_repo: FakePlayerRepository,
    ) -> None:
        """GET /api/player/me should return null handicap when no player."""
        response = client.get("/api/player/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["handicap"] is None


@allure.feature("REST API")
@allure.story("Player API")
class TestUpdateHandicapEndpoint:
    """Tests for PUT /api/player/handicap endpoint."""

    def test_update_handicap_without_auth_returns_401(
        self,
        client: TestClient,
        mock_users_collection: MagicMock,
    ) -> None:
        """PUT /api/player/handicap without authentication should return 401."""
        response = client.put(
            "/api/player/handicap",
            json={"handicap": "14.3"},
        )
        assert response.status_code == 401

    def test_update_handicap_valid_value(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
        override_player_repo: FakePlayerRepository,
    ) -> None:
        """PUT /api/player/handicap with valid value should update."""
        response = client.put(
            "/api/player/handicap",
            json={"handicap": "18.5"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Handicap updated successfully"

        # Verify the player was saved
        player = override_player_repo.find_by_user_id(str(TEST_USER_ID))
        assert player is not None
        assert player.handicap == Handicap(value=Decimal("18.5"))

    def test_update_handicap_to_null(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
        override_player_repo: FakePlayerRepository,
    ) -> None:
        """PUT /api/player/handicap with null should clear handicap."""
        # First set a handicap
        override_player_repo.save(
            Player(
                id=None,
                user_id=str(TEST_USER_ID),
                handicap=Handicap(value=Decimal("14.3")),
            )
        )

        response = client.put(
            "/api/player/handicap",
            json={"handicap": None},
            headers=auth_headers,
        )

        assert response.status_code == 200
        player = override_player_repo.find_by_user_id(str(TEST_USER_ID))
        assert player is not None
        assert player.handicap is None

    def test_update_handicap_invalid_value_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
        override_player_repo: FakePlayerRepository,
    ) -> None:
        """PUT /api/player/handicap with invalid value should return 400."""
        response = client.put(
            "/api/player/handicap",
            json={"handicap": "55.0"},
            headers=auth_headers,
        )

        assert response.status_code == 400
