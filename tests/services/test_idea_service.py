"""Tests for IdeaService."""

from unittest.mock import MagicMock

import allure
import pytest

from carry_on.domain.entities.idea import Idea, IdeaId
from carry_on.domain.repositories.idea_repository import IdeaRepository
from carry_on.services.idea_service import IdeaService


@allure.feature("Application Services")
@allure.story("Idea Service")
class TestIdeaServiceInit:
    """Tests for IdeaService initialization."""

    def test_init_accepts_repository(self) -> None:
        """IdeaService should accept a repository in constructor."""
        repository = MagicMock(spec=IdeaRepository)
        service = IdeaService(repository)
        assert service._repository is repository


@allure.feature("Application Services")
@allure.story("Idea Service")
class TestIdeaServiceRecordStroke:
    """Tests for IdeaService.record_idea() method."""

    def test_record_idea_returns_idea_id(self) -> None:
        """Should return IdeaId from repository."""
        repository = MagicMock(spec=IdeaRepository)
        expected_id = IdeaId(value="abc123")
        repository.save.return_value = expected_id
        service = IdeaService(repository)

        result = service.record_idea(
            user_id="user123",
            description="AsyncIO",
        )

        assert result == expected_id

    def test_record_idea_saves_correct_idea(self) -> None:
        """Should create and save an idea with correct attributes."""
        repository = MagicMock(spec=IdeaRepository)
        repository.save.return_value = IdeaId(value="abc123")
        service = IdeaService(repository)

        service.record_idea(
            user_id="user123",
            description="AsyncIO",
        )

        repository.save.assert_called_once()
        idea, user_id = repository.save.call_args[0]

        assert isinstance(idea, Idea)
        assert idea.description == "AsyncIO"
        assert user_id == "user123"

    def test_record_idea_without_description_raises_value_error(self) -> None:
        """Should raise ValueError for empty description."""
        repository = MagicMock(spec=IdeaRepository)
        service = IdeaService(repository)

        with pytest.raises(ValueError, match="Description is required"):
            service.record_idea(
                user_id="user123",
                description="",
            )

        repository.save.assert_not_called()
