"""Tests for StrokeService."""

from datetime import date
from unittest.mock import MagicMock

import allure
import pytest

from domain.entities.stroke import Stroke, StrokeId
from domain.repositories.stroke_repository import StrokeRepository
from domain.value_objects.club_type import ClubType
from domain.value_objects.distance import Distance
from services.stroke_service import StrokeService


@allure.feature("Application Services")
@allure.story("Stroke Service")
class TestStrokeServiceInit:
    """Tests for StrokeService initialization."""

    def test_init_accepts_repository(self) -> None:
        """StrokeService should accept a repository in constructor."""
        repository = MagicMock(spec=StrokeRepository)
        service = StrokeService(repository)
        assert service._repository is repository


@allure.feature("Application Services")
@allure.story("Stroke Service")
class TestStrokeServiceRecordStroke:
    """Tests for StrokeService.record_stroke() method."""

    def test_record_successful_stroke_returns_stroke_id(self) -> None:
        """Should return StrokeId from repository."""
        repository = MagicMock(spec=StrokeRepository)
        expected_id = StrokeId(value="abc123")
        repository.save.return_value = expected_id
        service = StrokeService(repository)

        result = service.record_stroke(
            user_id="user123",
            club="i7",
            stroke_date=date(2024, 1, 15),
            distance=150,
        )

        assert result == expected_id

    def test_record_successful_stroke_saves_correct_stroke(self) -> None:
        """Should create and save a successful stroke with correct attributes."""
        repository = MagicMock(spec=StrokeRepository)
        repository.save.return_value = StrokeId(value="abc123")
        service = StrokeService(repository)

        service.record_stroke(
            user_id="user123",
            club="i7",
            stroke_date=date(2024, 1, 15),
            distance=150,
        )

        repository.save.assert_called_once()
        stroke, user_id = repository.save.call_args[0]

        assert isinstance(stroke, Stroke)
        assert stroke.club == ClubType.IRON_7
        assert stroke.distance == Distance(meters=150)
        assert stroke.fail is False
        assert stroke.stroke_date == date(2024, 1, 15)
        assert user_id == "user123"

    def test_record_failed_stroke_returns_stroke_id(self) -> None:
        """Should return StrokeId for failed strokes."""
        repository = MagicMock(spec=StrokeRepository)
        expected_id = StrokeId(value="def456")
        repository.save.return_value = expected_id
        service = StrokeService(repository)

        result = service.record_stroke(
            user_id="user123",
            club="d",
            stroke_date=date(2024, 1, 15),
            fail=True,
        )

        assert result == expected_id

    def test_record_failed_stroke_saves_stroke_without_distance(self) -> None:
        """Should create and save a failed stroke with no distance."""
        repository = MagicMock(spec=StrokeRepository)
        repository.save.return_value = StrokeId(value="def456")
        service = StrokeService(repository)

        service.record_stroke(
            user_id="user123",
            club="d",
            stroke_date=date(2024, 1, 15),
            fail=True,
        )

        repository.save.assert_called_once()
        stroke, user_id = repository.save.call_args[0]

        assert stroke.club == ClubType.DRIVER
        assert stroke.distance is None
        assert stroke.fail is True
        assert user_id == "user123"

    def test_record_stroke_with_invalid_club_raises_value_error(self) -> None:
        """Should raise ValueError for invalid club codes."""
        repository = MagicMock(spec=StrokeRepository)
        service = StrokeService(repository)

        with pytest.raises(ValueError, match="'invalid' is not a valid ClubType"):
            service.record_stroke(
                user_id="user123",
                club="invalid",
                stroke_date=date(2024, 1, 15),
                distance=150,
            )

        repository.save.assert_not_called()

    def test_record_stroke_without_distance_for_success_raises_value_error(
        self,
    ) -> None:
        """Should raise ValueError when distance is missing for successful stroke."""
        repository = MagicMock(spec=StrokeRepository)
        service = StrokeService(repository)

        with pytest.raises(ValueError, match="Distance required when not a fail"):
            service.record_stroke(
                user_id="user123",
                club="i7",
                stroke_date=date(2024, 1, 15),
                # distance is None by default, fail is False by default
            )

        repository.save.assert_not_called()


@allure.feature("Application Services")
@allure.story("Stroke Service")
class TestStrokeServiceGetUserStrokes:
    """Tests for StrokeService.get_user_strokes() method."""

    def test_get_user_strokes_delegates_to_repository(self) -> None:
        """Should delegate to repository with correct parameters."""
        repository = MagicMock(spec=StrokeRepository)
        expected_strokes = [
            Stroke.create_successful(
                club=ClubType.IRON_7,
                distance=Distance(meters=150),
                stroke_date=date(2024, 1, 15),
                id=StrokeId(value="abc123"),
            )
        ]
        repository.find_by_user.return_value = expected_strokes
        service = StrokeService(repository)

        result = service.get_user_strokes("user123")

        assert result == expected_strokes
        repository.find_by_user.assert_called_once_with("user123", 20)

    def test_get_user_strokes_with_custom_limit(self) -> None:
        """Should pass custom limit to repository."""
        repository = MagicMock(spec=StrokeRepository)
        repository.find_by_user.return_value = []
        service = StrokeService(repository)

        service.get_user_strokes("user123", limit=10)

        repository.find_by_user.assert_called_once_with("user123", 10)

    def test_get_user_strokes_returns_empty_list_when_no_strokes(self) -> None:
        """Should return empty list when user has no strokes."""
        repository = MagicMock(spec=StrokeRepository)
        repository.find_by_user.return_value = []
        service = StrokeService(repository)

        result = service.get_user_strokes("user123")

        assert result == []
