"""Tests for Stroke entity."""

from datetime import date

import pytest

from domain.entities.stroke import Stroke, StrokeId
from domain.value_objects.club_type import ClubType
from domain.value_objects.distance import Distance


class TestStrokeId:
    """Tests for StrokeId value object."""

    def test_create_stroke_id(self) -> None:
        """Should create StrokeId with value."""
        stroke_id = StrokeId(value="abc123")
        assert stroke_id.value == "abc123"

    def test_stroke_id_equality(self) -> None:
        """StrokeIds with same value should be equal."""
        id1 = StrokeId(value="abc123")
        id2 = StrokeId(value="abc123")
        assert id1 == id2

    def test_stroke_id_immutable(self) -> None:
        """StrokeId should be immutable."""
        stroke_id = StrokeId(value="abc123")
        with pytest.raises(AttributeError):
            stroke_id.value = "new"  # type: ignore[misc]


class TestStrokeCreationSuccessful:
    """Tests for creating successful strokes."""

    def test_create_successful_stroke(self) -> None:
        """Should create successful stroke with distance."""
        stroke = Stroke.create_successful(
            club=ClubType.IRON_7,
            distance=Distance(meters=150),
            stroke_date=date(2024, 1, 15),
        )
        assert stroke.club == ClubType.IRON_7
        assert stroke.distance == Distance(meters=150)
        assert stroke.fail is False
        assert stroke.stroke_date == date(2024, 1, 15)
        assert stroke.id is None

    def test_create_successful_stroke_with_id(self) -> None:
        """Should create successful stroke with provided ID."""
        stroke_id = StrokeId(value="stroke123")
        stroke = Stroke.create_successful(
            club=ClubType.DRIVER,
            distance=Distance(meters=250),
            stroke_date=date(2024, 1, 15),
            id=stroke_id,
        )
        assert stroke.id == stroke_id

    def test_successful_stroke_requires_distance(self) -> None:
        """Successful stroke without distance should raise error."""
        with pytest.raises(ValueError, match="Distance required"):
            Stroke(
                id=None,
                club=ClubType.IRON_7,
                fail=False,
                stroke_date=date(2024, 1, 15),
                distance=None,
            )


class TestStrokeCreationFailed:
    """Tests for creating failed strokes."""

    def test_create_failed_stroke(self) -> None:
        """Should create failed stroke without distance."""
        stroke = Stroke.create_failed(
            club=ClubType.DRIVER,
            stroke_date=date(2024, 1, 15),
        )
        assert stroke.club == ClubType.DRIVER
        assert stroke.distance is None
        assert stroke.fail is True
        assert stroke.stroke_date == date(2024, 1, 15)

    def test_create_failed_stroke_with_id(self) -> None:
        """Should create failed stroke with provided ID."""
        stroke_id = StrokeId(value="fail123")
        stroke = Stroke.create_failed(
            club=ClubType.DRIVER,
            stroke_date=date(2024, 1, 15),
            id=stroke_id,
        )
        assert stroke.id == stroke_id

    def test_failed_stroke_ignores_distance(self) -> None:
        """Failed stroke should have no distance even if provided."""
        stroke = Stroke(
            id=None,
            club=ClubType.DRIVER,
            fail=True,
            stroke_date=date(2024, 1, 15),
            distance=Distance(meters=100),  # Should be ignored
        )
        assert stroke.distance is None


class TestStrokeAttributes:
    """Tests for Stroke attribute access."""

    def test_stroke_has_all_required_attributes(self) -> None:
        """Stroke should expose all required attributes."""
        stroke = Stroke.create_successful(
            club=ClubType.PITCHING_WEDGE,
            distance=Distance(meters=100),
            stroke_date=date(2024, 6, 1),
        )
        assert hasattr(stroke, "id")
        assert hasattr(stroke, "club")
        assert hasattr(stroke, "fail")
        assert hasattr(stroke, "stroke_date")
        assert hasattr(stroke, "distance")


class TestStrokeEquality:
    """Tests for Stroke equality (if applicable)."""

    def test_strokes_with_same_id_are_equal(self) -> None:
        """Strokes with same ID should be considered equal."""
        id1 = StrokeId(value="same")
        stroke1 = Stroke.create_successful(
            id=id1,
            club=ClubType.IRON_7,
            distance=Distance(meters=150),
            stroke_date=date(2024, 1, 15),
        )
        stroke2 = Stroke.create_successful(
            id=id1,
            club=ClubType.IRON_7,
            distance=Distance(meters=150),
            stroke_date=date(2024, 1, 15),
        )
        assert stroke1 == stroke2
