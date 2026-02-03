"""Step definitions for profile display feature."""

from typing import Any

import pytest
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from carry_on.api.password_security import hash_password
from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.login_page import LoginPage
from tests.acceptance.pages.navigation_page import NavigationPage

# Link this file to the feature file
scenarios("../features/navigation/profile.feature")


@pytest.fixture
def nav_page(page: Page, base_url: str) -> NavigationPage:
    """Create a NavigationPage instance for the test."""
    return NavigationPage(page, base_url)


@given(
    parsers.parse(
        'a user exists with email "{email}" and password "{password}" and display name '
        '"{display_name}"'
    ),
    target_fixture="test_user",
)
def user_with_display_name(
    test_database: Database[Any], email: str, password: str, display_name: str
) -> dict[str, Any]:
    """Create an activated user with a display name in the database."""
    pin_hash = hash_password(password)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email=email,
        display_name=display_name,
        pin_hash=pin_hash,
        activated_at=activated_at,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": display_name,
        "pin_hash": pin_hash,
        "activated_at": activated_at,
        "password": password,
    }


@given(parsers.parse('I am logged in as "{email}" with password "{password}"'))
def logged_in(login_page: LoginPage, email: str, password: str) -> None:
    """Perform login with given credentials."""
    login_page.goto_login()
    login_page.enter_email(email)
    login_page.click_continue()
    login_page.wait_for_pin_step()
    login_page.enter_pin(password)
    login_page.click_submit()
    login_page.wait_for_logged_in()


@when("I click the Profile tab")
def click_profile_tab(nav_page: NavigationPage) -> None:
    """Click the Profile tab."""
    nav_page.click_profile_tab()
    nav_page.wait_for_profile_loaded()


@when("I click the logout button")
def click_logout(nav_page: NavigationPage) -> None:
    """Click the logout button."""
    nav_page.click_logout()


@when("I reload the page")
def reload_page(nav_page: NavigationPage) -> None:
    """Reload the page."""
    nav_page.reload()


@then(parsers.parse('I should see my display name "{display_name}"'))
def see_display_name(nav_page: NavigationPage, display_name: str) -> None:
    """Verify the display name is shown."""
    actual_name = nav_page.get_profile_name()
    assert display_name in actual_name, f"Expected '{display_name}' in '{actual_name}'"


@then(parsers.parse('I should see my email "{email}"'))
def see_email(nav_page: NavigationPage, email: str) -> None:
    """Verify the email is shown."""
    actual_email = nav_page.get_profile_email()
    assert email in actual_email, f"Expected '{email}' in '{actual_email}'"


@then("I should see the logout button")
def see_logout_button(nav_page: NavigationPage) -> None:
    """Verify the logout button is visible."""
    assert nav_page.is_logout_button_visible(), "Logout button should be visible"


@then("I should see the login screen")
def see_login_screen(nav_page: NavigationPage) -> None:
    """Verify login screen is visible."""
    nav_page.page.wait_for_timeout(500)
    assert nav_page.is_login_screen_visible(), "Login screen should be visible"


@then("the tab bar should not be visible")
def tab_bar_not_visible(nav_page: NavigationPage) -> None:
    """Verify the tab bar is not visible."""
    nav_page.page.wait_for_timeout(500)
    assert not nav_page.is_tab_bar_visible(), "Tab bar should not be visible"
