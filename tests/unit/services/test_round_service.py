"""Tests for RoundService."""

import datetime
from unittest.mock import MagicMock

import allure
import pytest

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.services.round_service import RoundService


def _sample_holes(n: int) -> list[dict]:
    """Helper to create a list of raw hole result dicts."""
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


@allure.feature("Application Services")
@allure.story("Round Service")
class TestRoundServiceCreateRound:
    """Tests for RoundService.create_round() method."""

    def test_create_round_returns_round_id(self) -> None:
        """Should return RoundId from repository."""
        repository = MagicMock(spec=RoundRepository)
        expected_id = RoundId(value="round-123")
        repository.save.return_value = expected_id
        service = RoundService(repository)

        result = service.create_round(
            user_id="user123",
            course_name="Pitch & Putt",
            date="2026-02-01",
            holes=_sample_holes(9),
        )

        assert result == expected_id

    def test_create_round_saves_round_with_correct_data(self) -> None:
        """Should create and save a Round with correct attributes."""
        repository = MagicMock(spec=RoundRepository)
        repository.save.return_value = RoundId(value="round-123")
        service = RoundService(repository)

        service.create_round(
            user_id="user123",
            course_name="Pitch & Putt",
            date="2026-02-01",
            holes=_sample_holes(9),
        )

        repository.save.assert_called_once()
        round, user_id = repository.save.call_args[0]

        assert isinstance(round, Round)
        assert round.course == "Pitch & Putt"
        assert round.date == datetime.date(2026, 2, 1)
        assert user_id == "user123"

    def test_create_round_records_all_holes(self) -> None:
        """Should record all hole results on the round."""
        repository = MagicMock(spec=RoundRepository)
        repository.save.return_value = RoundId(value="round-123")
        service = RoundService(repository)

        service.create_round(
            user_id="user123",
            course_name="Test Course",
            date="2026-02-01",
            holes=_sample_holes(9),
        )

        round, _ = repository.save.call_args[0]
        assert len(round.holes) == 9
        assert all(isinstance(h, HoleResult) for h in round.holes)
        assert round.holes[0].hole_number == 1
        assert round.holes[0].strokes == 4

    def test_create_round_with_empty_course_raises(self) -> None:
        """Should raise ValueError for empty course name."""
        repository = MagicMock(spec=RoundRepository)
        service = RoundService(repository)

        with pytest.raises(ValueError, match="Course name required"):
            service.create_round(
                user_id="user123",
                course_name="",
                date="2026-02-01",
                holes=_sample_holes(9),
            )

        repository.save.assert_not_called()


@allure.feature("Application Services")
@allure.story("Round Service")
class TestRoundServiceGetUserRounds:
    """Tests for RoundService.get_user_rounds() method."""

    def test_get_user_rounds_returns_rounds(self) -> None:
        """Should return rounds from repository."""
        repository = MagicMock(spec=RoundRepository)
        expected_rounds = [
            Round.create(
                course="Test Course",
                date=datetime.date(2026, 2, 1),
                id=RoundId(value="r1"),
            ),
        ]
        repository.find_by_user.return_value = expected_rounds
        service = RoundService(repository)

        result = service.get_user_rounds("user123")

        assert len(result) == 1
        assert result[0].course == "Test Course"
        repository.find_by_user.assert_called_once_with("user123")

    def test_get_user_rounds_returns_empty_list(self) -> None:
        """Should return empty list when user has no rounds."""
        repository = MagicMock(spec=RoundRepository)
        repository.find_by_user.return_value = []
        service = RoundService(repository)

        result = service.get_user_rounds("user123")

        assert result == []
