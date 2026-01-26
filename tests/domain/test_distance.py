"""Tests for Distance value object."""

import pytest

from domain.value_objects.distance import Distance


class TestDistanceCreation:
    """Tests for Distance creation and validation."""

    def test_create_valid_distance(self) -> None:
        """Should create Distance with valid meters value."""
        distance = Distance(meters=150)
        assert distance.meters == 150

    def test_create_zero_distance(self) -> None:
        """Zero meters should be valid (for chip shots near hole)."""
        distance = Distance(meters=0)
        assert distance.meters == 0

    def test_create_max_distance(self) -> None:
        """Maximum distance (400m) should be valid."""
        distance = Distance(meters=400)
        assert distance.meters == 400

    def test_negative_distance_raises_error(self) -> None:
        """Negative distance should raise ValueError."""
        with pytest.raises(ValueError, match="Distance must be"):
            Distance(meters=-1)

    def test_exceeds_max_distance_raises_error(self) -> None:
        """Distance exceeding 400m should raise ValueError."""
        with pytest.raises(ValueError, match="Distance must be"):
            Distance(meters=401)


class TestDistanceImmutability:
    """Tests for Distance immutability (value object property)."""

    def test_distance_is_frozen(self) -> None:
        """Distance should be immutable (frozen dataclass)."""
        distance = Distance(meters=150)
        with pytest.raises(AttributeError):
            distance.meters = 200  # type: ignore[misc]


class TestDistanceEquality:
    """Tests for Distance equality comparison."""

    def test_equal_distances(self) -> None:
        """Distances with same meters should be equal."""
        d1 = Distance(meters=150)
        d2 = Distance(meters=150)
        assert d1 == d2

    def test_unequal_distances(self) -> None:
        """Distances with different meters should not be equal."""
        d1 = Distance(meters=150)
        d2 = Distance(meters=151)
        assert d1 != d2

    def test_hashable(self) -> None:
        """Distance should be hashable (usable in sets/dicts)."""
        d1 = Distance(meters=150)
        d2 = Distance(meters=150)
        distance_set = {d1, d2}
        assert len(distance_set) == 1


class TestDistanceConstants:
    """Tests for Distance class constants."""

    def test_min_meters_constant(self) -> None:
        """MIN_METERS should be 0."""
        assert Distance.MIN_METERS == 0

    def test_max_meters_constant(self) -> None:
        """MAX_METERS should be 400."""
        assert Distance.MAX_METERS == 400
