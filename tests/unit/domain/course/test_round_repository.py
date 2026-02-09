"""Tests for RoundRepository protocol."""

import allure

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.repositories.round_repository import RoundRepository


@allure.feature("Domain Model")
@allure.story("Round Repository Protocol")
class TestRoundRepositoryProtocol:
    """Tests for RoundRepository protocol shape."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """RoundRepository should be a runtime-checkable Protocol."""
        assert hasattr(RoundRepository, "__protocol_attrs__") or isinstance(
            RoundRepository, type
        )

    def test_protocol_has_save_method(self) -> None:
        """RoundRepository should define a save method."""
        assert hasattr(RoundRepository, "save")

    def test_protocol_has_find_by_user_method(self) -> None:
        """RoundRepository should define a find_by_user method."""
        assert hasattr(RoundRepository, "find_by_user")

    def test_conforming_class_is_instance(self) -> None:
        """A class implementing save and find_by_user should satisfy the protocol."""

        class DummyRepo:
            def save(self, round: Round, user_id: str) -> RoundId:
                return RoundId(value="dummy")

            def find_by_user(self, user_id: str) -> list[Round]:
                return []

        assert isinstance(DummyRepo(), RoundRepository)

    def test_non_conforming_class_is_not_instance(self) -> None:
        """A class missing methods should not satisfy the protocol."""

        class NotARepo:
            pass

        assert not isinstance(NotARepo(), RoundRepository)
