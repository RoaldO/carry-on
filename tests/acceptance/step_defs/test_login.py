"""Step definitions for login feature."""

from typing import Any

from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import hash_password
from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/auth/login.feature")


@given(
    parsers.parse('a user exists with email "{email}" and password "{password}"'),
    target_fixture="test_user",
)
def user_with_password(
    test_database: Database[Any], email: str, password: str
) -> dict[str, Any]:
    """Create an activated user with a password in the database."""
    password_hash = hash_password(password)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email=email,
        display_name="Active User",
        password_hash=password_hash,
        activated_at=activated_at,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": "Active User",
        "password_hash": password_hash,
        "activated_at": activated_at,
        "password": password,
    }


@then("I should see the password login form")
def see_login_form(login_page: LoginPage) -> None:
    """Verify the password login form is visible (not activation)."""
    login_page.wait_for_pin_step()
    assert not login_page.is_confirm_pin_visible(), "Confirm should not be visible"
    assert login_page.get_submit_button_text() == "Login"


@then(parsers.parse('the submit button should say "{text}"'))
def submit_button_text(login_page: LoginPage, text: str) -> None:
    """Verify the submit button text."""
    actual_text = login_page.get_submit_button_text()
    assert text == actual_text, f"Expected '{text}' but got '{actual_text}'"


@then("the confirm password field should not be visible")
def confirm_password_not_visible(login_page: LoginPage) -> None:
    """Verify the confirm password field is hidden."""
    assert not login_page.is_confirm_pin_visible(), "Confirm password should be hidden"


@when("I reload the page")
def reload_page(login_page: LoginPage) -> None:
    """Reload the page."""
    login_page.reload()


@then("I should still be logged in")
def still_logged_in(login_page: LoginPage) -> None:
    """Verify user is still logged in after reload."""
    # Wait a moment for the page to check localStorage and auto-login
    login_page.page.wait_for_timeout(1000)
    assert login_page.is_login_screen_hidden(), "Should still be logged in after reload"
