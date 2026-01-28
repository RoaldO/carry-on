"""Tests for ClubType value object."""

import json
from enum import Enum

import allure
import pytest

from carry_on.domain.value_objects.club_type import ClubType


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
class TestClubTypeEnum:
    """Tests for ClubType enum definition."""

    def test_club_type_is_enum(self) -> None:
        """ClubType should be an Enum."""
        assert issubclass(ClubType, Enum)

    def test_club_type_is_str_enum(self) -> None:
        """ClubType should inherit from str for JSON serialization."""
        assert issubclass(ClubType, str)

    @pytest.mark.parametrize(
        "enum_value, expectation",
        [
            (ClubType.DRIVER, "d"),
            (ClubType.WOOD_3, "3w"),
            (ClubType.WOOD_5, "5w"),
            (ClubType.HYBRID_4, "4h"),
            (ClubType.HYBRID_5, "5h"),
            (ClubType.IRON_5, "5i"),
            (ClubType.IRON_6, "6i"),
            (ClubType.IRON_7, "7i"),
            (ClubType.IRON_8, "8i"),
            (ClubType.IRON_9, "9i"),
            (ClubType.PITCHING_WEDGE, "pw"),
            (ClubType.GAP_WEDGE, "gw"),
            (ClubType.SAND_WEDGE, "sw"),
            (ClubType.LOB_WEDGE, "lw"),
        ],
    )
    def test_club_type_enum_values(self, enum_value, expectation) -> None:
        """Club types should have correct values."""
        assert enum_value.value == expectation


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
class TestClubTypeStringComparison:
    """Tests for ClubType string comparison behavior."""

    def test_club_type_equals_string_value(self) -> None:
        """ClubType should equal its string value."""
        assert ClubType.DRIVER == "d"
        assert ClubType.IRON_7 == "7i"

    def test_club_type_value_attribute(self) -> None:
        """ClubType.value should return the string value."""
        assert ClubType.DRIVER.value == "d"
        assert ClubType.IRON_7.value == "7i"


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
class TestClubTypeJsonSerialization:
    """Tests for ClubType JSON serialization."""

    def test_json_serialize(self) -> None:
        """ClubType should serialize to JSON as its string value."""
        data = {"club": ClubType.DRIVER}
        serialized = json.dumps(data)
        assert serialized == '{"club": "d"}'

    def test_json_deserialize_to_club_type(self) -> None:
        """JSON string value should convert to ClubType."""
        club = ClubType("d")
        assert club == ClubType.DRIVER

    def test_invalid_value_raises_error(self) -> None:
        """Invalid string value should raise ValueError."""
        with pytest.raises(ValueError):
            ClubType("invalid")


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
class TestClubTypeLookup:
    """Tests for ClubType lookup by value."""

    def test_lookup_by_value(self) -> None:
        """Should be able to look up ClubType by string value."""
        assert ClubType("d") == ClubType.DRIVER
        assert ClubType("3w") == ClubType.WOOD_3
        assert ClubType("pw") == ClubType.PITCHING_WEDGE

    def test_all_clubs_are_unique(self) -> None:
        """All club type values should be unique."""
        values = [club.value for club in ClubType]
        assert len(values) == len(set(values))

    def test_total_club_count(self) -> None:
        """Should have 14 club types (standard golf bag)."""
        assert len(ClubType) == 14
