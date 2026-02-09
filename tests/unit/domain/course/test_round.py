from datetime import date

import allure
import pytest

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.value_objects.hole_result import HoleResult


@allure.feature("Domain Model")
@allure.story("Round Aggregate")
class TestRoundCreation:
    def test_create_round(self) -> None:
        """Should create round with a course."""
        round = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round.course == "Old Course, St Andrews Links, Scotland"
        assert round.date == date(2024, 1, 15)
        assert round.id is None

    def test_create_round_with_id(self) -> None:
        """Should create successful stroke with provided ID."""
        round_id = RoundId(value="round123")
        round = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            id=round_id,
        )
        assert round.id == round_id

    def test_round_requires_a_course_name(self) -> None:
        """Successful stroke without distance should raise error."""
        with pytest.raises(ValueError, match="Course name required"):
            Round(
                id=None,
                course="",
                date=date(2024, 1, 15),
            )


@allure.feature("Domain Model")
@allure.story("Round Entity")
class TestRoundAttributes:
    def test_round_has_all_required_attributes(self) -> None:
        """Round should expose all required attributes."""
        stroke = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert hasattr(stroke, "id")
        assert hasattr(stroke, "course")
        assert hasattr(stroke, "date")


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Holes")
class TestRoundHoles:
    def test_new_round_starts_with_empty_holes(self) -> None:
        """A newly created round should have no hole results."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.holes == []

    def test_record_hole_adds_hole_result(self) -> None:
        """Recording a hole should add it to the round's holes."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        round_.record_hole(hole)
        assert len(round_.holes) == 1
        assert round_.holes[0] == hole

    def test_record_hole_rejects_duplicate_hole_number(self) -> None:
        """Recording the same hole number twice should raise an error."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        round_.record_hole(hole)
        duplicate = HoleResult(hole_number=1, strokes=5, par=4, stroke_index=7)
        with pytest.raises(ValueError, match="Hole 1 already recorded"):
            round_.record_hole(duplicate)

    def test_total_strokes_returns_sum(self) -> None:
        """Total strokes should be the sum of all recorded hole strokes."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7))
        round_.record_hole(HoleResult(hole_number=2, strokes=3, par=3, stroke_index=15))
        round_.record_hole(HoleResult(hole_number=3, strokes=5, par=5, stroke_index=3))
        assert round_.total_strokes == 12

    def test_total_strokes_returns_zero_when_no_holes(self) -> None:
        """Total strokes should be 0 for a round with no recorded holes."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.total_strokes == 0

    def test_is_complete_returns_false_when_fewer_than_18_holes(self) -> None:
        """A round with fewer than 18 holes is not complete."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7))
        assert round_.is_complete is False

    def test_is_complete_returns_true_when_all_18_holes_recorded(self) -> None:
        """A round with all 18 holes recorded is complete."""
        round_ = Round.create(
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        assert round_.is_complete is True

    def test_direct_constructor_starts_with_empty_holes(self) -> None:
        """Round created via direct constructor should also have empty holes."""
        round_ = Round(
            id=None,
            course="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.holes == []
