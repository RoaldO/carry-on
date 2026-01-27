"""Step definitions for registration feature."""

from typing import Any
from unittest.mock import MagicMock

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/auth/registration.feature")


@given(
    parsers.parse('a user exists with email "{email}" who needs activation'),
    target_fixture="test_user",
)
def user_needs_activation(
    mock_collections: dict[str, MagicMock], email: str
) -> dict[str, Any]:
    """Create an inactive user in the mock database."""
    user = {
        "_id": f"user_{email.replace('@', '_')}",
        "email": email,
        "display_name": "Inactive User",
        "pin_hash": None,
        "activated_at": None,
    }

    original_side_effect = mock_collections["users"].find_one.side_effect

    def find_one(query: dict) -> dict | None:
        if query.get("email") == email:
            return user
        if original_side_effect:
            return original_side_effect(query)
        return None

    mock_collections["users"].find_one.side_effect = find_one
    return user


@then("I should see the PIN activation form")
def see_activation_form(login_page: LoginPage) -> None:
    """Verify the PIN activation form is visible."""
    login_page.wait_for_pin_step()
    assert login_page.is_confirm_pin_visible(), "Confirm PIN field should be visible"
    assert login_page.get_submit_button_text() == "Activate"


@when("I click the back button")
def click_back(login_page: LoginPage) -> None:
    """Click the back button."""
    login_page.click_back()


@then("I should see the email form")
def see_email_form(login_page: LoginPage) -> None:
    """Verify the email form is visible."""
    login_page.wait_for_email_step()
    assert login_page.is_email_step_visible(), "Email step should be visible"
