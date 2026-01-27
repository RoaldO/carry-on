"""Tests for ClubType value object."""

import json
from enum import Enum

import allure
import pytest

from domain.value_objects.club_type import ClubType


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
def test_club_type_is_enum() -> None:
    """ClubType should be an Enum."""
    assert issubclass(ClubType, Enum)


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
def test_club_type_is_str_enum() -> None:
    """ClubType should inherit from str for JSON serialization."""
    assert issubclass(ClubType, str)


_club_type_enum_values = [
    (ClubType.DRIVER, "d"),
    (ClubType.WOOD_3, "3w"),
    (ClubType.WOOD_5, "5w"),
    (ClubType.HYBRID_4, "h4"),
    (ClubType.HYBRID_5, "h5"),
    (ClubType.IRON_5, "i5"),
    (ClubType.IRON_6, "i6"),
    (ClubType.IRON_7, "i7"),
    (ClubType.IRON_8, "i8"),
    (ClubType.IRON_9, "i9"),
    (ClubType.PITCHING_WEDGE, "pw"),
    (ClubType.GAP_WEDGE, "gw"),
    (ClubType.SAND_WEDGE, "sw"),
    (ClubType.LOB_WEDGE, "lw"),
]
_club_value_enum_types = [
    (str_value, enum_value)
    for enum_value, str_value in _club_type_enum_values
]

@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
@pytest.mark.parametrize('enum_value, expectation', _club_type_enum_values)
def test_club_type_enum_values_match(enum_value, expectation) -> None:
    """Club types should have correct values."""
    assert enum_value == expectation


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
@pytest.mark.parametrize('enum_value, expectation', _club_type_enum_values)
def test_club_type_enum_embedded_values_match(enum_value, expectation) -> None:
    """Club types should have correct values."""
    assert enum_value.value == expectation


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
@pytest.mark.parametrize('enum_value, expectation', _club_type_enum_values)
def test_json_serialize(enum_value, expectation) -> None:
    """ClubType should serialize to JSON as its string value."""
    data = {"club": enum_value}
    serialized = json.dumps(data)
    assert serialized == f'{{"club": "{expectation}"}}'


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
@pytest.mark.parametrize('str_value, expectation', _club_value_enum_types)
def test_json_deserialize_to_club_type(str_value, expectation) -> None:
    """JSON string value should convert to ClubType."""
    club = ClubType(str_value)
    assert club == expectation


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
def test_invalid_value_raises_error() -> None:
    """Invalid string value should raise ValueError."""
    with pytest.raises(ValueError):
        ClubType("invalid")


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
def test_all_clubs_are_unique() -> None:
    """All club type values should be unique."""
    values = [club.value for club in ClubType]
    assert len(values) == len(set(values))


@allure.feature("Domain Model")
@allure.story("ClubType Value Object")
def test_total_club_count() -> None:
    """Should have 14 club types (standard golf bag)."""
    assert len(ClubType) == 14
