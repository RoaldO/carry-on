"""Tests for Ideas API endpoints (FR-1 to FR-6, NFR-1, NFR-2)."""

from unittest.mock import MagicMock

import allure
from fastapi.testclient import TestClient

from tests.unit.conftest import TEST_USER_ID


@allure.feature("REST API")
@allure.story("Ideas API")
class TestIdeasEndpoint:
    """Tests for ideas API endpoints."""

    def test_post_idea_without_auth_returns_401(
        self, client: TestClient, mock_users_collection: MagicMock
    ) -> None:
        """POST /api/ideas without authentication should return 401 (NFR-1)."""
        response = client.post(
            "/api/ideas",
            json={"description": "Add dark mode"},
        )
        assert response.status_code == 401

    def test_post_idea_with_valid_auth(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/ideas with valid authentication should create idea (FR-3, FR-4)."""
        response = client.post(
            "/api/ideas",
            json={"description": "Add dark mode"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Idea submitted successfully"
        assert data["idea"]["description"] == "Add dark mode"

    def test_post_idea_without_description_returns_422(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/ideas without description should return 422 (FR-2)."""
        response = client.post(
            "/api/ideas",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_post_idea_with_empty_description_returns_422(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/ideas with empty description should return 422 (FR-2)."""
        response = client.post(
            "/api/ideas",
            json={"description": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_post_idea_with_description_over_1000_chars_returns_422(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/ideas with description > 1000 chars should return 422 (FR-2)."""
        long_description = "a" * 1001
        response = client.post(
            "/api/ideas",
            json={"description": long_description},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_post_idea_with_description_exactly_1000_chars(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/ideas with exactly 1000 chars should succeed (FR-2)."""
        description = "a" * 1000
        response = client.post(
            "/api/ideas",
            json={"description": description},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_post_idea_stores_user_id(
        self,
        client: TestClient,
        auth_headers: dict[str, str],
        mock_ideas_collection: MagicMock,
        mock_authenticated_user: MagicMock,
    ) -> None:
        """POST /api/ideas should store user_id in the document."""
        response = client.post(
            "/api/ideas",
            json={"description": "Add dark mode"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify insert_one was called with user_id
        call_args = mock_ideas_collection.insert_one.call_args
        inserted_doc = call_args[0][0]
        assert "user_id" in inserted_doc
        assert inserted_doc["user_id"] == str(TEST_USER_ID)
