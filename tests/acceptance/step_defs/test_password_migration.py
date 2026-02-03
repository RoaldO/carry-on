"""Step definitions for password migration feature."""

from typing import Any

from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from carry_on.api.password_security import hash_password
from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/auth/password_migration.feature")


@given(
    parsers.parse(
        'a user exists with email "{email}" and weak password "{password}"'
    ),
    target_fixture="test_user",
)
def user_with_weak_password(
    test_database: Database[Any], email: str, password: str
) -> dict[str, Any]:
    """Create an activated user with a weak password in the database."""
    password_hash = hash_password(password)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email=email,
        display_name="Migration Test User",
        password_hash=password_hash,
        activated_at=activated_at,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": "Migration Test User",
        "password_hash": password_hash,
        "activated_at": activated_at,
        "password": password,
    }


@then("I should see the password update form")
def see_password_update_form(login_page: LoginPage) -> None:
    """Verify the password update form is visible."""
    login_page.wait_for_update_password_step()
    assert login_page.is_update_password_step_visible(), (
        "Password update step should be visible"
    )


@when(parsers.parse('I enter new password "{password}"'))
def enter_new_password(login_page: LoginPage, password: str) -> None:
    """Enter new password in the new password field."""
    login_page.enter_new_password(password)


@when(parsers.parse('I confirm new password "{password}"'))
def confirm_new_password(login_page: LoginPage, password: str) -> None:
    """Enter password in the confirm new password field."""
    login_page.enter_confirm_new_password(password)


@when("I click update password")
def click_update_password(login_page: LoginPage) -> None:
    """Click the update password button."""
    login_page.click_update_password()


@then("I should be logged in")
def should_be_logged_in(login_page: LoginPage) -> None:
    """Verify user is logged in (login screen hidden)."""
    login_page.wait_for_logged_in()
    assert login_page.is_login_screen_hidden(), "Should be logged in"


@then("I should see password mismatch error")
def see_password_mismatch_error(login_page: LoginPage) -> None:
    """Verify password mismatch error is shown."""
    login_page.wait_for_update_password_error()
    error = login_page.get_update_password_error()
    assert "match" in error.lower(), f"Expected mismatch error, got: {error}"
