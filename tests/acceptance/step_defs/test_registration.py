"""Step definitions for registration feature."""

from typing import Any

from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/auth/registration.feature")


@given(
    parsers.parse('a user exists with email "{email}" who needs activation'),
    target_fixture="test_user",
)
def user_needs_activation(test_database: Database[Any], email: str) -> dict[str, Any]:
    """Create an inactive user in the database."""
    user_id = insert_user(
        test_database,
        email=email,
        display_name="Inactive User",
        pin_hash=None,
        activated_at=None,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": "Inactive User",
        "pin_hash": None,
        "activated_at": None,
    }


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
