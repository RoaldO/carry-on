from dataclasses import FrozenInstanceError

import allure
import pytest

from carry_on.domain.course.value_objects.hole_result import HoleResult


@allure.feature("Domain Model")
@allure.story("HoleResult Value Object")
class TestHoleResultCreation:
    def test_create_valid_hole_result(self) -> None:
        """Should create a HoleResult with valid values."""
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        assert hole.hole_number == 1
        assert hole.strokes == 4
        assert hole.par == 4
        assert hole.stroke_index == 7

    def test_hole_result_is_immutable(self) -> None:
        """HoleResult should be frozen (immutable value object)."""
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        with pytest.raises(FrozenInstanceError):
            hole.strokes = 5  # type: ignore[misc]

    def test_hole_results_with_same_values_are_equal(self) -> None:
        """Two HoleResults with identical values should be equal."""
        hole_a = HoleResult(hole_number=3, strokes=5, par=4, stroke_index=11)
        hole_b = HoleResult(hole_number=3, strokes=5, par=4, stroke_index=11)
        assert hole_a == hole_b

    def test_hole_results_with_different_values_are_not_equal(self) -> None:
        """Two HoleResults with different values should not be equal."""
        hole_a = HoleResult(hole_number=3, strokes=5, par=4, stroke_index=11)
        hole_b = HoleResult(hole_number=3, strokes=4, par=4, stroke_index=11)
        assert hole_a != hole_b


@allure.feature("Domain Model")
@allure.story("HoleResult Value Object")
class TestHoleResultValidation:
    def test_hole_number_must_be_at_least_1(self) -> None:
        """Hole number 0 is invalid."""
        with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
            HoleResult(hole_number=0, strokes=4, par=4, stroke_index=7)

    def test_hole_number_must_be_at_most_18(self) -> None:
        """Hole number 19 is invalid."""
        with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
            HoleResult(hole_number=19, strokes=4, par=4, stroke_index=7)

    def test_strokes_allows_zero_for_in_progress_holes(self) -> None:
        """Zero strokes is valid for in-progress holes (club tally mode)."""
        hole = HoleResult(hole_number=1, strokes=0, par=4, stroke_index=7)
        assert hole.strokes == 0

    def test_strokes_rejects_negative(self) -> None:
        """Negative strokes is always invalid."""
        with pytest.raises(ValueError, match="Strokes must not be negative"):
            HoleResult(hole_number=1, strokes=-1, par=4, stroke_index=7)

    def test_par_must_be_3_4_or_5(self) -> None:
        """Par must be one of the standard values: 3, 4, or 5."""
        with pytest.raises(ValueError, match="Par must be 3, 4, or 5"):
            HoleResult(hole_number=1, strokes=4, par=2, stroke_index=7)

    def test_par_6_is_invalid(self) -> None:
        """Par 6 is not a standard par value."""
        with pytest.raises(ValueError, match="Par must be 3, 4, or 5"):
            HoleResult(hole_number=1, strokes=4, par=6, stroke_index=7)

    def test_stroke_index_must_be_at_least_1(self) -> None:
        """Stroke index 0 is invalid."""
        with pytest.raises(ValueError, match="Stroke index must be between 1 and 18"):
            HoleResult(hole_number=1, strokes=4, par=4, stroke_index=0)

    def test_stroke_index_must_be_at_most_18(self) -> None:
        """Stroke index 19 is invalid."""
        with pytest.raises(ValueError, match="Stroke index must be between 1 and 18"):
            HoleResult(hole_number=1, strokes=4, par=4, stroke_index=19)


@allure.feature("Domain Model")
@allure.story("HoleResult Value Object - Stableford Points")
class TestHoleResultStablefordPoints:
    """Tests for the optional stableford_points field on HoleResult."""

    def test_stableford_points_defaults_to_none(self) -> None:
        """HoleResult without explicit points should default to None."""
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        assert hole.stableford_points is None

    def test_stableford_points_stored(self) -> None:
        """HoleResult with explicit points should preserve the value."""
        hole = HoleResult(
            hole_number=1, strokes=4, par=4, stroke_index=7, stableford_points=2
        )
        assert hole.stableford_points == 2


@allure.feature("Domain Model")
@allure.story("HoleResult Value Object - Clubs Used")
class TestHoleResultClubsUsed:
    """Tests for the optional clubs_used field on HoleResult."""

    def test_clubs_used_defaults_to_none(self) -> None:
        """HoleResult without clubs_used should default to None."""
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        assert hole.clubs_used is None

    def test_clubs_used_accepts_matching_tuple(self) -> None:
        """clubs_used tuple length must match strokes count."""
        hole = HoleResult(
            hole_number=1,
            strokes=3,
            par=4,
            stroke_index=7,
            clubs_used=("d", "7i", "pw"),
        )
        assert hole.clubs_used == ("d", "7i", "pw")

    def test_clubs_used_rejects_mismatched_length(self) -> None:
        """clubs_used with wrong length should raise ValueError."""
        with pytest.raises(ValueError, match="clubs_used length must match strokes"):
            HoleResult(
                hole_number=1,
                strokes=2,
                par=4,
                stroke_index=7,
                clubs_used=("d", "7i", "pw"),
            )

    def test_clubs_used_accepts_empty_tuple_for_zero_strokes(self) -> None:
        """Empty tuple is valid for 0-stroke in-progress holes."""
        hole = HoleResult(
            hole_number=1,
            strokes=0,
            par=4,
            stroke_index=7,
            clubs_used=(),
        )
        assert hole.clubs_used == ()

    def test_clubs_used_none_with_nonzero_strokes(self) -> None:
        """None clubs_used is valid with any stroke count (simple counter mode)."""
        hole = HoleResult(
            hole_number=1,
            strokes=5,
            par=4,
            stroke_index=7,
            clubs_used=None,
        )
        assert hole.clubs_used is None
