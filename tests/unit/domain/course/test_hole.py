import allure
import pytest

from carry_on.domain.course.value_objects.hole import Hole


@allure.feature("Domain Model")
@allure.story("Hole Value Object")
class TestHoleCreation:
    def test_create_valid_hole(self) -> None:
        """Should create a hole with valid attributes."""
        hole = Hole(hole_number=1, par=4, stroke_index=7)
        assert hole.hole_number == 1
        assert hole.par == 4
        assert hole.stroke_index == 7

    def test_hole_is_immutable(self) -> None:
        """Hole should be a frozen dataclass."""
        hole = Hole(hole_number=1, par=4, stroke_index=7)
        with pytest.raises(AttributeError):
            hole.par = 5  # type: ignore[misc]


@allure.feature("Domain Model")
@allure.story("Hole Value Object - Validation")
class TestHoleValidation:
    def test_rejects_hole_number_zero(self) -> None:
        """Hole number 0 is invalid."""
        with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
            Hole(hole_number=0, par=4, stroke_index=1)

    def test_rejects_hole_number_nineteen(self) -> None:
        """Hole number 19 is invalid."""
        with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
            Hole(hole_number=19, par=4, stroke_index=1)

    def test_rejects_negative_hole_number(self) -> None:
        """Negative hole number is invalid."""
        with pytest.raises(ValueError, match="Hole number must be between 1 and 18"):
            Hole(hole_number=-1, par=4, stroke_index=1)

    def test_rejects_par_two(self) -> None:
        """Par 2 is invalid."""
        with pytest.raises(ValueError, match="Par must be 3, 4, or 5"):
            Hole(hole_number=1, par=2, stroke_index=1)

    def test_rejects_par_six(self) -> None:
        """Par 6 is invalid."""
        with pytest.raises(ValueError, match="Par must be 3, 4, or 5"):
            Hole(hole_number=1, par=6, stroke_index=1)

    def test_rejects_stroke_index_zero(self) -> None:
        """Stroke index 0 is invalid."""
        with pytest.raises(ValueError, match="Stroke index must be between 1 and 18"):
            Hole(hole_number=1, par=4, stroke_index=0)

    def test_rejects_stroke_index_nineteen(self) -> None:
        """Stroke index 19 is invalid."""
        with pytest.raises(ValueError, match="Stroke index must be between 1 and 18"):
            Hole(hole_number=1, par=4, stroke_index=19)
