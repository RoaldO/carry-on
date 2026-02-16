"""Tests for RoundStatus value object."""

import json
from enum import Enum

import allure
import pytest

from carry_on.domain.course.value_objects.round_status import RoundStatus


@allure.feature("Domain Model")
@allure.story("RoundStatus Value Object")
class TestRoundStatusEnum:
    """Tests for RoundStatus enum definition."""

    def test_round_status_is_enum(self) -> None:
        """RoundStatus should be an Enum."""
        assert issubclass(RoundStatus, Enum)

    def test_round_status_is_str_enum(self) -> None:
        """RoundStatus should inherit from str for JSON serialization."""
        assert issubclass(RoundStatus, str)

    @pytest.mark.parametrize(
        "enum_value, expectation",
        [
            (RoundStatus.IN_PROGRESS, "ip"),
            (RoundStatus.FINISHED, "f"),
            (RoundStatus.ABORTED, "a"),
        ],
    )
    def test_round_status_enum_values(self, enum_value, expectation) -> None:
        """Round statuses should have correct short string values."""
        assert enum_value.value == expectation


@allure.feature("Domain Model")
@allure.story("RoundStatus Value Object")
class TestRoundStatusStringComparison:
    """Tests for RoundStatus string comparison behavior."""

    def test_round_status_equals_string_value(self) -> None:
        """RoundStatus should equal its string value."""
        assert RoundStatus.IN_PROGRESS == "ip"
        assert RoundStatus.FINISHED == "f"
        assert RoundStatus.ABORTED == "a"

    def test_round_status_value_attribute(self) -> None:
        """RoundStatus.value should return the string value."""
        assert RoundStatus.IN_PROGRESS.value == "ip"
        assert RoundStatus.FINISHED.value == "f"
        assert RoundStatus.ABORTED.value == "a"


@allure.feature("Domain Model")
@allure.story("RoundStatus Value Object")
class TestRoundStatusJsonSerialization:
    """Tests for RoundStatus JSON serialization."""

    def test_json_serialize(self) -> None:
        """RoundStatus should serialize to JSON as its string value."""
        data = {"status": RoundStatus.IN_PROGRESS}
        serialized = json.dumps(data)
        assert serialized == '{"status": "ip"}'

    def test_json_deserialize_to_round_status(self) -> None:
        """JSON string value should convert to RoundStatus."""
        status = RoundStatus("ip")
        assert status == RoundStatus.IN_PROGRESS

    def test_invalid_value_raises_error(self) -> None:
        """Invalid string value should raise ValueError."""
        with pytest.raises(ValueError):
            RoundStatus("invalid")


@allure.feature("Domain Model")
@allure.story("RoundStatus Value Object")
class TestRoundStatusLookup:
    """Tests for RoundStatus lookup by value."""

    def test_lookup_by_value(self) -> None:
        """Should be able to look up RoundStatus by string value."""
        assert RoundStatus("ip") == RoundStatus.IN_PROGRESS
        assert RoundStatus("f") == RoundStatus.FINISHED
        assert RoundStatus("a") == RoundStatus.ABORTED

    def test_all_statuses_are_unique(self) -> None:
        """All status values should be unique."""
        values = [status.value for status in RoundStatus]
        assert len(values) == len(set(values))

    def test_total_status_count(self) -> None:
        """Should have exactly 3 round statuses."""
        assert len(RoundStatus) == 3
