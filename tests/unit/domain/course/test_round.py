from datetime import date

import allure
import pytest

from carry_on.domain.course.aggregates.round import Round, RoundId


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
