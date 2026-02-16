"""Tests for RoundService."""

import datetime
from unittest.mock import MagicMock

import allure
import pytest

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.round_status import RoundStatus
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
        assert round.course_name == "Pitch & Putt"
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
                course_name="Test Course",
                date=datetime.date(2026, 2, 1),
                id=RoundId(value="r1"),
            ),
        ]
        repository.find_by_user.return_value = expected_rounds
        service = RoundService(repository)

        result = service.get_user_rounds("user123")

        assert len(result) == 1
        assert result[0].course_name == "Test Course"
        repository.find_by_user.assert_called_once_with("user123")

    def test_get_user_rounds_returns_empty_list(self) -> None:
        """Should return empty list when user has no rounds."""
        repository = MagicMock(spec=RoundRepository)
        repository.find_by_user.return_value = []
        service = RoundService(repository)

        result = service.get_user_rounds("user123")

        assert result == []


@allure.feature("Application Services")
@allure.story("Round Service")
class TestRoundServiceCreateRoundPartial:
    """Tests for creating rounds with partial holes."""

    def test_create_round_with_no_holes(self) -> None:
        """Should create a round with no holes for incremental saving."""
        repository = MagicMock(spec=RoundRepository)
        expected_id = RoundId(value="round-123")
        repository.save.return_value = expected_id
        service = RoundService(repository)

        result = service.create_round(
            user_id="user123",
            course_name="Pitch & Putt",
            date="2026-02-01",
            holes=[],
        )

        assert result == expected_id
        repository.save.assert_called_once()
        round, user_id = repository.save.call_args[0]
        assert len(round.holes) == 0
        assert user_id == "user123"


@allure.feature("Application Services")
@allure.story("Round Service")
class TestRoundServiceUpdateHole:
    """Tests for RoundService.update_hole() method."""

    def test_update_hole_result(self) -> None:
        """Should update an existing hole in a round."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")

        # Existing round with one hole
        existing_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        existing_round.record_hole(
            HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1)
        )
        repository.find_by_id.return_value = existing_round
        repository.save.return_value = round_id

        service = RoundService(repository)

        service.update_hole(
            user_id="user123",
            round_id=round_id,
            hole={"hole_number": 1, "strokes": 5, "par": 4, "stroke_index": 1},
        )

        repository.find_by_id.assert_called_once_with(round_id, "user123")
        repository.save.assert_called_once()

        # Verify the round was updated
        saved_round, user_id = repository.save.call_args[0]
        assert saved_round.holes[0].strokes == 5

    def test_update_hole_records_new_hole(self) -> None:
        """Should record a new hole if it doesn't exist yet."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")

        # Existing round with no holes
        existing_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        repository.find_by_id.return_value = existing_round
        repository.save.return_value = round_id

        service = RoundService(repository)

        service.update_hole(
            user_id="user123",
            round_id=round_id,
            hole={"hole_number": 1, "strokes": 4, "par": 4, "stroke_index": 1},
        )

        # Verify the hole was recorded
        saved_round, _ = repository.save.call_args[0]
        assert len(saved_round.holes) == 1
        assert saved_round.holes[0].strokes == 4

    def test_update_hole_raises_when_round_not_found(self) -> None:
        """Should raise ValueError when round doesn't exist."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="nonexistent")
        repository.find_by_id.return_value = None

        service = RoundService(repository)

        with pytest.raises(ValueError, match="Round nonexistent not found"):
            service.update_hole(
                user_id="user123",
                round_id=round_id,
                hole={"hole_number": 1, "strokes": 4, "par": 4, "stroke_index": 1},
            )

        repository.save.assert_not_called()


@allure.feature("Application Services")
@allure.story("Round Service")
class TestRoundServiceGetRound:
    """Tests for RoundService.get_round() method."""

    def test_get_round_by_id(self) -> None:
        """Should return a round by ID."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")
        expected_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        repository.find_by_id.return_value = expected_round

        service = RoundService(repository)
        result = service.get_round(user_id="user123", round_id=round_id)

        assert result == expected_round
        repository.find_by_id.assert_called_once_with(round_id, "user123")

    def test_get_round_returns_none_when_not_found(self) -> None:
        """Should return None when round doesn't exist."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="nonexistent")
        repository.find_by_id.return_value = None

        service = RoundService(repository)
        result = service.get_round(user_id="user123", round_id=round_id)

        assert result is None


@allure.feature("Application Services")
@allure.story("Round Service - Status")
class TestRoundServiceUpdateStatus:
    """Tests for RoundService.update_round_status() method."""

    def test_update_round_status_finish(self) -> None:
        """Should call finish() method on the round."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")

        # Existing round in IN_PROGRESS state
        existing_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        repository.find_by_id.return_value = existing_round
        repository.save.return_value = round_id

        service = RoundService(repository)
        service.update_round_status(
            user_id="user123",
            round_id=round_id,
            action="finish",
        )

        repository.find_by_id.assert_called_once_with(round_id, "user123")
        repository.save.assert_called_once()

        # Verify the round was finished
        saved_round, user_id = repository.save.call_args[0]
        assert saved_round.status == RoundStatus.FINISHED

    def test_update_round_status_abort(self) -> None:
        """Should call abort() method on the round."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")

        # Existing round in IN_PROGRESS state
        existing_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        repository.find_by_id.return_value = existing_round
        repository.save.return_value = round_id

        service = RoundService(repository)
        service.update_round_status(
            user_id="user123",
            round_id=round_id,
            action="abort",
        )

        # Verify the round was aborted
        saved_round, _ = repository.save.call_args[0]
        assert saved_round.status == RoundStatus.ABORTED

    def test_update_round_status_resume(self) -> None:
        """Should call resume() method on the round."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")

        # Existing round in ABORTED state
        existing_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
            status=RoundStatus.ABORTED,
        )
        repository.find_by_id.return_value = existing_round
        repository.save.return_value = round_id

        service = RoundService(repository)
        service.update_round_status(
            user_id="user123",
            round_id=round_id,
            action="resume",
        )

        # Verify the round was resumed
        saved_round, _ = repository.save.call_args[0]
        assert saved_round.status == RoundStatus.IN_PROGRESS

    def test_update_round_status_invalid_action_raises(self) -> None:
        """Should raise ValueError for invalid action."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="round-123")

        existing_round = Round.create(
            course_name="Pitch & Putt",
            date=datetime.date(2026, 2, 1),
            id=round_id,
        )
        repository.find_by_id.return_value = existing_round

        service = RoundService(repository)

        with pytest.raises(ValueError, match="Invalid action: invalid"):
            service.update_round_status(
                user_id="user123",
                round_id=round_id,
                action="invalid",
            )

        repository.save.assert_not_called()

    def test_update_round_status_round_not_found_raises(self) -> None:
        """Should raise ValueError when round doesn't exist."""
        repository = MagicMock(spec=RoundRepository)
        round_id = RoundId(value="nonexistent")
        repository.find_by_id.return_value = None

        service = RoundService(repository)

        with pytest.raises(ValueError, match="Round nonexistent not found"):
            service.update_round_status(
                user_id="user123",
                round_id=round_id,
                action="finish",
            )

        repository.save.assert_not_called()
