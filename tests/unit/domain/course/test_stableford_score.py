import allure
import pytest

from carry_on.domain.course.value_objects.stableford_score import StablefordScore


@allure.feature("Domain Model")
@allure.story("StablefordScore Value Object")
class TestStablefordScoreCreation:
    def test_create_with_valid_points(self) -> None:
        """Should create a StablefordScore with the given points."""
        score = StablefordScore(points=36)
        assert score.points == 36

    def test_create_with_zero_points(self) -> None:
        """Zero is a valid Stableford score."""
        score = StablefordScore(points=0)
        assert score.points == 0


@allure.feature("Domain Model")
@allure.story("StablefordScore Value Object - Immutability")
class TestStablefordScoreImmutability:
    def test_is_frozen(self) -> None:
        """StablefordScore should be immutable (frozen dataclass)."""
        score = StablefordScore(points=36)
        with pytest.raises(AttributeError):
            score.points = 40  # type: ignore[misc]


@allure.feature("Domain Model")
@allure.story("StablefordScore Value Object - Equality")
class TestStablefordScoreEquality:
    def test_equal_by_value(self) -> None:
        """Two scores with the same points should be equal."""
        assert StablefordScore(points=36) == StablefordScore(points=36)

    def test_not_equal_different_points(self) -> None:
        """Scores with different points should not be equal."""
        assert StablefordScore(points=36) != StablefordScore(points=30)


@allure.feature("Domain Model")
@allure.story("StablefordScore Value Object - Validation")
class TestStablefordScoreValidation:
    def test_rejects_negative_points(self) -> None:
        """Negative points are not valid."""
        with pytest.raises(ValueError, match="Points must not be negative"):
            StablefordScore(points=-1)
