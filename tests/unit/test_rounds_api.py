"""Tests for rounds API using dependency injection."""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from tests.fakes.fake_round_repository import FakeRoundRepository
from tests.unit.conftest import TEST_USER_ID


def _sample_holes(n: int) -> list[dict]:
    """Helper to create a list of raw hole result dicts for n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4]
    return [
        {
            "hole_number": i + 1,
            "strokes": 4,
            "par": pars[i % len(pars)],
            "stroke_index": i + 1,
        }
        for i in range(n)
    ]


@allure.feature("REST API")
@allure.story("Rounds API")
class TestRoundsWithDependencyInjection:
    """Tests for rounds endpoints using DI with fake repository."""

    def test_post_round_saves_to_repository(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds should save round via injected repository."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Round recorded successfully"
        assert "id" in data

        # Verify round was saved to the fake repository
        assert len(override_round_repo.rounds) == 1
        saved_round, user_id = override_round_repo.rounds[0]
        assert saved_round.course_name == "Pitch & Putt"
        assert len(saved_round.holes) == 9
        assert user_id == str(TEST_USER_ID)

    def test_post_round_with_empty_course_returns_400(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/rounds with empty course should return 400."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_post_round_without_auth_returns_401(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        mock_users_collection: MagicMock,
    ) -> None:
        """POST /api/rounds without auth should return 401."""
        response = client.post(
            "/api/rounds",
            json={
                "course_name": "Test",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
        )

        assert response.status_code == 401

    def test_get_rounds_returns_saved_rounds(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should return rounds from repository."""
        # Create a round first
        client.post(
            "/api/rounds",
            json={
                "course_name": "Pitch & Putt",
                "date": "2026-02-01",
                "holes": _sample_holes(9),
            },
            headers=auth_headers,
        )

        # Retrieve
        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["rounds"]) == 1
        assert data["rounds"][0]["course_name"] == "Pitch & Putt"

    def test_get_rounds_returns_empty_list(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/rounds should return empty list when no rounds exist."""
        response = client.get("/api/rounds", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["rounds"] == []

    def test_get_rounds_without_auth_returns_401(
        self,
        client: TestClient,
        override_round_repo: FakeRoundRepository,
        mock_users_collection: MagicMock,
    ) -> None:
        """GET /api/rounds without auth should return 401."""
        response = client.get("/api/rounds")

        assert response.status_code == 401
