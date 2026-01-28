"""Tests for strokes API using dependency injection.

These tests use FakeStrokeRepository injected via FastAPI's dependency
overrides, demonstrating proper DI testing patterns without mocking
MongoDB internals.
"""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from tests.fakes.fake_stroke_repository import FakeStrokeRepository


@allure.feature("REST API")
@allure.story("Strokes API")
class TestStrokesWithDependencyInjection:
    """Tests for strokes endpoints using DI with fake repository."""

    def test_post_stroke_saves_to_repository(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes should save stroke via injected repository."""
        client, fake_repo = client_with_fake_repo

        response = client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Stroke recorded successfully"

        # Verify stroke was saved to the fake repository
        assert len(fake_repo.strokes) == 1
        saved_stroke, user_id = fake_repo.strokes[0]
        assert saved_stroke.club.value == "7i"
        assert saved_stroke.distance is not None
        assert saved_stroke.distance.meters == 150
        assert saved_stroke.fail is False
        assert user_id == "user123"

    def test_post_failed_stroke_saves_without_distance(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes with fail=true should save without distance."""
        client, fake_repo = client_with_fake_repo

        response = client.post(
            "/api/strokes",
            json={"club": "d", "fail": True},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify stroke was saved as failed
        assert len(fake_repo.strokes) == 1
        saved_stroke, _ = fake_repo.strokes[0]
        assert saved_stroke.club.value == "d"
        assert saved_stroke.distance is None
        assert saved_stroke.fail is True

    def test_get_strokes_returns_saved_strokes(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes should return strokes from repository."""
        client, fake_repo = client_with_fake_repo

        # First, create some strokes
        client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
            headers=auth_headers,
        )
        client.post(
            "/api/strokes",
            json={"club": "d", "distance": 250},
            headers=auth_headers,
        )

        # Now retrieve them
        response = client.get("/api/strokes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["strokes"]) == 2

        # Strokes should be newest first
        clubs = [s["club"] for s in data["strokes"]]
        assert "7i" in clubs
        assert "d" in clubs

    def test_get_strokes_filters_by_user(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes should only return strokes for authenticated user."""
        client, fake_repo = client_with_fake_repo

        # Create a stroke for authenticated user
        client.post(
            "/api/strokes",
            json={"club": "7i", "distance": 150},
            headers=auth_headers,
        )

        # Manually add a stroke for different user directly to repository
        from datetime import date

        from carry_on.domain.entities.stroke import Stroke
        from carry_on.domain.value_objects.club_type import ClubType
        from carry_on.domain.value_objects.distance import Distance

        other_user_stroke = Stroke.create_successful(
            club=ClubType.DRIVER,
            distance=Distance(meters=300),
            stroke_date=date.today(),
        )
        fake_repo.save(other_user_stroke, user_id="other_user_456")

        # Verify both strokes are in repository
        assert len(fake_repo.strokes) == 2

        # GET should only return strokes for authenticated user
        response = client.get("/api/strokes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["strokes"][0]["club"] == "7i"

    def test_get_strokes_respects_limit(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes should respect limit parameter."""
        client, fake_repo = client_with_fake_repo

        # Create 5 strokes
        for i in range(5):
            client.post(
                "/api/strokes",
                json={"club": "7i", "distance": 100 + i * 10},
                headers=auth_headers,
            )

        # Request with limit=3
        response = client.get("/api/strokes?limit=3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["strokes"]) == 3

    def test_stroke_response_includes_created_at(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """GET /api/strokes should include created_at in response."""
        client, fake_repo = client_with_fake_repo

        # Create a stroke
        client.post(
            "/api/strokes",
            json={"club": "pw", "distance": 100},
            headers=auth_headers,
        )

        # Retrieve it
        response = client.get("/api/strokes", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["strokes"]) == 1
        stroke = data["strokes"][0]
        assert "created_at" in stroke
        assert stroke["created_at"] is not None
        # Verify it's an ISO format datetime string
        assert "T" in stroke["created_at"]

    def test_invalid_club_returns_400(
        self,
        client_with_fake_repo: tuple[TestClient, FakeStrokeRepository],
        auth_headers: dict[str, str],
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/strokes with invalid club should return 400."""
        client, fake_repo = client_with_fake_repo

        response = client.post(
            "/api/strokes",
            json={"club": "invalid_club", "distance": 150},
            headers=auth_headers,
        )

        assert response.status_code == 400
        # Repository should be empty
        assert len(fake_repo.strokes) == 0
