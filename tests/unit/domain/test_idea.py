"""Tests for Idea entity."""

from datetime import datetime, timezone

import allure
import pytest

from carry_on.domain.entities.idea import Idea, IdeaId


@allure.feature("Domain Model")
@allure.story("Idea Entity")
class TestIdeaId:
    """Tests for IdeaId value object."""

    def test_create_idea_id(self) -> None:
        """Should create IdeaId with value."""
        idea_id = IdeaId(value="abc123")
        assert idea_id.value == "abc123"

    def test_idea_id_equality(self) -> None:
        """IdeaIds with same value should be equal."""
        id1 = IdeaId(value="abc123")
        id2 = IdeaId(value="abc123")
        assert id1 == id2

    def test_idea_id_immutable(self) -> None:
        """StrokeId should be immutable."""
        idea_id = IdeaId(value="abc123")
        with pytest.raises(AttributeError):
            idea_id.value = "new"  # type: ignore[misc]


@allure.feature("Domain Model")
@allure.story("Idea Entity")
class TestStrokeCreationSuccessful:
    """Tests for creating ideas."""

    def test_create_idea(self) -> None:
        """Should create idea."""
        idea = Idea.create_idea(
            description="AsynchIO support for better performance",
        )
        assert idea.description == "AsynchIO support for better performance"
        assert idea.id is None

    def test_create_successful_stroke_with_id(self) -> None:
        """Should create successful stroke with provided ID."""
        idea_id = IdeaId(value="idea123")
        idea = Idea.create_idea(
            id=idea_id,
            description="AsynchIO support for better performance",
        )
        assert idea.id == idea_id


@allure.feature("Domain Model")
@allure.story("Idea Entity")
class TestIdeaAttributes:
    """Tests for Idea attribute access."""

    def test_stroke_has_all_required_attributes(self) -> None:
        """Stroke should expose all required attributes."""
        idea = Idea.create_idea(
            description="AsynchIO support for better performance",
        )
        assert hasattr(idea, "id")
        assert hasattr(idea, "description")
        assert hasattr(idea, "created_at")


@allure.feature("Domain Model")
@allure.story("Idea Entity")
class TestIdeaEquality:
    """Tests for Idea equality (if applicable)."""

    def test_idea_with_same_id_are_equal(self) -> None:
        """Ideas with same ID should be considered equal."""
        id1 = IdeaId(value="same")
        idea1 = Idea.create_idea(
            id=id1,
            description="AsynchIO support for better performance",
        )
        idea2 = Idea.create_idea(
            id=id1,
            description="AsynchIO support for better performance",
        )
        assert idea1 == idea2


@allure.feature("Domain Model")
@allure.story("Idea Entity")
class TestIdeaCreatedAt:
    """Tests for created_at field on ideas."""

    def test_idea_with_created_at(self) -> None:
        """Should preserve created_at in successful idea factory."""
        created = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        idea = Idea.create_idea(
            description="AsynchIO support for better performance",
            created_at=created,
        )
        assert idea.created_at == created

    def test_created_at_defaults_to_none(self) -> None:
        """New strokes should have created_at as None by default."""
        idea = Idea.create_idea(
            description="AsynchIO support for better performance",
        )
        assert idea.created_at is None

    def test_idea_direct_construction_with_created_at(self) -> None:
        """Should allow created_at via direct construction."""
        created = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        idea = Idea(
            id=None,
            description="AsynchIO support for better performance",
            created_at=created,
        )
        assert idea.created_at == created
