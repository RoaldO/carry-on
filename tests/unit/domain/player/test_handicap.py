"""Tests for Handicap value object."""

from decimal import Decimal

import allure
import pytest

from carry_on.domain.player.value_objects.handicap import Handicap


@allure.feature("Domain Model")
@allure.story("Handicap Value Object")
class TestHandicapCreation:
    """Tests for Handicap creation and validation."""

    def test_create_valid_handicap(self) -> None:
        """Should create Handicap with a typical value like 14.3."""
        handicap = Handicap(value=Decimal("14.3"))
        assert handicap.value == Decimal("14.3")

    def test_create_zero_handicap(self) -> None:
        """Zero handicap (scratch golfer) should be valid."""
        handicap = Handicap(value=Decimal("0"))
        assert handicap.value == Decimal("0")

    def test_create_plus_handicap(self) -> None:
        """Negative value represents a plus handicap (better than scratch)."""
        handicap = Handicap(value=Decimal("-2.5"))
        assert handicap.value == Decimal("-2.5")

    def test_create_max_handicap(self) -> None:
        """Maximum WHS handicap (54.0) should be valid."""
        handicap = Handicap(value=Decimal("54.0"))
        assert handicap.value == Decimal("54.0")

    def test_create_min_handicap(self) -> None:
        """Minimum WHS handicap (-10.0) should be valid."""
        handicap = Handicap(value=Decimal("-10.0"))
        assert handicap.value == Decimal("-10.0")

    def test_exceeds_max_raises_error(self) -> None:
        """Handicap above 54.0 should raise ValueError."""
        with pytest.raises(ValueError, match="Handicap must be"):
            Handicap(value=Decimal("54.1"))

    def test_below_min_raises_error(self) -> None:
        """Handicap below -10.0 should raise ValueError."""
        with pytest.raises(ValueError, match="Handicap must be"):
            Handicap(value=Decimal("-10.1"))


@allure.feature("Domain Model")
@allure.story("Handicap Value Object")
class TestHandicapImmutability:
    """Tests for Handicap immutability (value object property)."""

    def test_handicap_is_frozen(self) -> None:
        """Handicap should be immutable (frozen dataclass)."""
        handicap = Handicap(value=Decimal("14.3"))
        with pytest.raises(AttributeError):
            handicap.value = Decimal("20.0")  # type: ignore[misc]


@allure.feature("Domain Model")
@allure.story("Handicap Value Object")
class TestHandicapEquality:
    """Tests for Handicap equality comparison."""

    def test_equal_handicaps(self) -> None:
        """Handicaps with same value should be equal."""
        h1 = Handicap(value=Decimal("14.3"))
        h2 = Handicap(value=Decimal("14.3"))
        assert h1 == h2

    def test_unequal_handicaps(self) -> None:
        """Handicaps with different values should not be equal."""
        h1 = Handicap(value=Decimal("14.3"))
        h2 = Handicap(value=Decimal("14.4"))
        assert h1 != h2

    def test_hashable(self) -> None:
        """Handicap should be hashable (usable in sets/dicts)."""
        h1 = Handicap(value=Decimal("14.3"))
        h2 = Handicap(value=Decimal("14.3"))
        handicap_set = {h1, h2}
        assert len(handicap_set) == 1


@allure.feature("Domain Model")
@allure.story("Handicap Value Object")
class TestHandicapConstants:
    """Tests for Handicap class constants."""

    def test_min_value_constant(self) -> None:
        """MIN_VALUE should be -10.0."""
        assert Handicap.MIN_VALUE == Decimal("-10.0")

    def test_max_value_constant(self) -> None:
        """MAX_VALUE should be 54.0."""
        assert Handicap.MAX_VALUE == Decimal("54.0")
