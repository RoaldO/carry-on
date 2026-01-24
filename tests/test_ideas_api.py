"""Tests for Ideas API endpoints (FR-1 to FR-6, NFR-1, NFR-2)."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient


class TestIdeasEndpoint:
    """Tests for ideas API endpoints."""

    def test_post_idea_without_pin_returns_401(self, client: TestClient) -> None:
        """POST /api/ideas without PIN should return 401 (NFR-1)."""
        response = client.post(
            "/api/ideas",
            json={"description": "Add dark mode"},
        )
        assert response.status_code == 401

    def test_post_idea_with_valid_pin(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
    ) -> None:
        """POST /api/ideas with valid PIN should create idea (FR-3, FR-4)."""
        response = client.post(
            "/api/ideas",
            json={"description": "Add dark mode"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Idea submitted successfully"
        assert data["idea"]["description"] == "Add dark mode"
        assert "created_at" in data["idea"]

    def test_post_idea_without_description_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
    ) -> None:
        """POST /api/ideas without description should return 400 (FR-2)."""
        response = client.post(
            "/api/ideas",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_post_idea_with_empty_description_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
    ) -> None:
        """POST /api/ideas with empty description should return 400 (FR-2)."""
        response = client.post(
            "/api/ideas",
            json={"description": ""},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_post_idea_with_description_over_1000_chars_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
    ) -> None:
        """POST /api/ideas with description > 1000 chars should return 400 (FR-2)."""
        long_description = "a" * 1001
        response = client.post(
            "/api/ideas",
            json={"description": long_description},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_post_idea_with_description_exactly_1000_chars(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
    ) -> None:
        """POST /api/ideas with exactly 1000 chars should succeed (FR-2)."""
        description = "a" * 1000
        response = client.post(
            "/api/ideas",
            json={"description": description},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_ideas_without_pin_returns_401(self, client: TestClient) -> None:
        """GET /api/ideas without PIN should return 401 (NFR-1)."""
        response = client.get("/api/ideas")
        assert response.status_code == 401

    def test_get_ideas_with_valid_pin(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
    ) -> None:
        """GET /api/ideas with valid PIN should return ideas."""
        response = client.get("/api/ideas", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "ideas" in data
        assert "count" in data
