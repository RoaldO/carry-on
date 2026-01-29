"""Step definitions for login feature."""

from typing import Any
from unittest.mock import MagicMock

from pytest_bdd import given, parsers, scenarios, then, when

from carry_on.api.pin_security import hash_pin
from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/auth/login.feature")


@given(
    parsers.parse('a user exists with email "{email}" and PIN "{pin}"'),
    target_fixture="test_user",
)
def user_with_pin(
    mock_collections: dict[str, MagicMock], email: str, pin: str
) -> dict[str, Any]:
    """Create an activated user with a PIN in the mock database."""
    user = {
        "_id": f"user_{email.replace('@', '_')}",
        "email": email,
        "display_name": "Active User",
        "pin_hash": hash_pin(pin),
        "activated_at": "2026-01-25T10:00:00Z",
    }

    original_side_effect = mock_collections["users"].find_one.side_effect

    def find_one(query: dict) -> dict | None:
        if query.get("email") == email:
            return user
        if original_side_effect:
            return original_side_effect(query)
        return None

    mock_collections["users"].find_one.side_effect = find_one
    return {**user, "pin": pin}


@then("I should see the PIN login form")
def see_login_form(login_page: LoginPage) -> None:
    """Verify the PIN login form is visible (not activation)."""
    login_page.wait_for_pin_step()
    assert not login_page.is_confirm_pin_visible(), "Confirm PIN should not be visible"
    assert login_page.get_submit_button_text() == "Login"


@then(parsers.parse('the submit button should say "{text}"'))
def submit_button_text(login_page: LoginPage, text: str) -> None:
    """Verify the submit button text."""
    actual_text = login_page.get_submit_button_text()
    assert text == actual_text, f"Expected '{text}' but got '{actual_text}'"


@then("the confirm PIN field should not be visible")
def confirm_pin_not_visible(login_page: LoginPage) -> None:
    """Verify the confirm PIN field is hidden."""
    assert not login_page.is_confirm_pin_visible(), "Confirm PIN should be hidden"


@when("I reload the page")
def reload_page(login_page: LoginPage) -> None:
    """Reload the page."""
    login_page.reload()


@then("I should still be logged in")
def still_logged_in(login_page: LoginPage) -> None:
    """Verify user is still logged in after reload."""
    # Wait a moment for the page to check localStorage and auto-login
    login_page.page.wait_for_timeout(1000)
    # DELIBERATELY BROKEN: This will fail to test screenshot capture
    assert not login_page.is_login_screen_hidden(), "DELIBERATE FAILURE for screenshot test"
