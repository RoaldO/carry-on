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

    def test_strokes_must_be_at_least_1(self) -> None:
        """Zero strokes is invalid — you must take at least one stroke."""
        with pytest.raises(ValueError, match="Strokes must be at least 1"):
            HoleResult(hole_number=1, strokes=0, par=4, stroke_index=7)

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
