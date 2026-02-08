import allure
import pytest

from carry_on.domain.core.value_objects.identifier import Identifier


@allure.feature("Core domain")
@allure.story("Identifier Value Object")
class TestIdentifier:
    def test_create_identifier(self) -> None:
        """Should create Identifier with value."""
        identifier = Identifier(value="abc123")
        assert identifier.value == "abc123"

    def test_identifier_equality(self) -> None:
        """Identifierss with same value should be equal."""
        identifier1 = Identifier(value="abc123")
        identifier2 = Identifier(value="abc123")
        assert identifier1 == identifier2

    def test_identifier_immutable(self) -> None:
        """Identifier should be immutable."""
        identifier = Identifier(value="abc123")
        with pytest.raises(AttributeError):
            identifier.value = "new"  # type: ignore[misc]
