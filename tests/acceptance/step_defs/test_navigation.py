"""Step definitions for tab navigation feature."""

from typing import Any

import pytest
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from carry_on.api.pin_security import hash_pin
from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.login_page import LoginPage
from tests.acceptance.pages.navigation_page import NavigationPage

# Link this file to the feature file
scenarios("../features/navigation/tabs.feature")


@pytest.fixture
def nav_page(page: Page, base_url: str) -> NavigationPage:
    """Create a NavigationPage instance for the test."""
    return NavigationPage(page, base_url)


@given(
    parsers.parse('a user exists with email "{email}" and PIN "{pin}"'),
    target_fixture="test_user",
)
def user_with_pin(test_database: Database[Any], email: str, pin: str) -> dict[str, Any]:
    """Create an activated user with a PIN in the database."""
    pin_hash = hash_pin(pin)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email=email,
        display_name="Navigation Test User",
        pin_hash=pin_hash,
        activated_at=activated_at,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": "Navigation Test User",
        "pin_hash": pin_hash,
        "activated_at": activated_at,
        "pin": pin,
    }


@given(parsers.parse('I am logged in as "{email}" with PIN "{pin}"'))
def logged_in(login_page: LoginPage, email: str, pin: str) -> None:
    """Perform login with given credentials."""
    login_page.goto_login()
    login_page.enter_email(email)
    login_page.click_continue()
    login_page.wait_for_pin_step()
    login_page.enter_pin(pin)
    login_page.click_submit()
    login_page.wait_for_logged_in()


@given("I am on the Strokes tab")
def on_strokes_tab(nav_page: NavigationPage) -> None:
    """Ensure we're on the Strokes tab."""
    if not nav_page.is_on_strokes_tab():
        nav_page.click_strokes_tab()
    assert nav_page.is_on_strokes_tab()


@given("I am on the Ideas tab")
def on_ideas_tab(nav_page: NavigationPage) -> None:
    """Ensure we're on the Ideas tab."""
    nav_page.click_ideas_tab()
    assert nav_page.is_on_ideas_tab()


@given("I am on the Profile tab")
def on_profile_tab(nav_page: NavigationPage) -> None:
    """Ensure we're on the Profile tab."""
    nav_page.click_profile_tab()
    nav_page.page.wait_for_timeout(500)
    assert nav_page.is_on_profile_tab()


@when("I click the Strokes tab")
def click_strokes_tab(nav_page: NavigationPage) -> None:
    """Click the Strokes tab."""
    nav_page.click_strokes_tab()


@when("I click the Ideas tab")
def click_ideas_tab(nav_page: NavigationPage) -> None:
    """Click the Ideas tab."""
    nav_page.click_ideas_tab()


@when("I click the Profile tab")
def click_profile_tab(nav_page: NavigationPage) -> None:
    """Click the Profile tab."""
    nav_page.click_profile_tab()
    nav_page.page.wait_for_timeout(500)


@when(parsers.parse('I navigate to "{hash_url}"'))
def navigate_to_hash(nav_page: NavigationPage, hash_url: str) -> None:
    """Navigate to a URL with hash."""
    nav_page.navigate_to_hash(hash_url)


@when("I logout")
def logout(nav_page: NavigationPage) -> None:
    """Click logout button."""
    nav_page.click_profile_tab()
    nav_page.page.wait_for_timeout(500)
    nav_page.click_logout()


@then("the tab bar should be visible")
def tab_bar_visible(nav_page: NavigationPage) -> None:
    """Verify the tab bar is visible."""
    assert nav_page.is_tab_bar_visible(), "Tab bar should be visible"


@then("the tab bar should not be visible")
def tab_bar_not_visible(nav_page: NavigationPage) -> None:
    """Verify the tab bar is not visible."""
    nav_page.page.wait_for_timeout(500)
    assert not nav_page.is_tab_bar_visible(), "Tab bar should not be visible"


@then("I should see the Strokes tab")
def see_strokes_tab(nav_page: NavigationPage) -> None:
    """Verify Strokes tab is visible."""
    assert nav_page.is_strokes_tab_visible(), "Strokes tab should be visible"


@then("I should see the Ideas tab")
def see_ideas_tab(nav_page: NavigationPage) -> None:
    """Verify Ideas tab is visible."""
    assert nav_page.is_ideas_tab_visible(), "Ideas tab should be visible"


@then("I should see the Profile tab")
def see_profile_tab(nav_page: NavigationPage) -> None:
    """Verify Profile tab is visible."""
    assert nav_page.is_profile_tab_visible(), "Profile tab should be visible"


@then("I should be on the Strokes tab")
def should_be_on_strokes_tab(nav_page: NavigationPage) -> None:
    """Verify Strokes content is visible."""
    nav_page.page.wait_for_timeout(300)
    assert nav_page.is_on_strokes_tab(), "Should be on Strokes tab"


@then("I should be on the Ideas tab")
def should_be_on_ideas_tab(nav_page: NavigationPage) -> None:
    """Verify Ideas content is visible."""
    nav_page.page.wait_for_timeout(300)
    assert nav_page.is_on_ideas_tab(), "Should be on Ideas tab"


@then("I should be on the Profile tab")
def should_be_on_profile_tab(nav_page: NavigationPage) -> None:
    """Verify Profile content is visible."""
    nav_page.page.wait_for_timeout(300)
    assert nav_page.is_on_profile_tab(), "Should be on Profile tab"


@then("the Strokes tab should be active")
def strokes_tab_active(nav_page: NavigationPage) -> None:
    """Verify Strokes tab is marked active."""
    assert nav_page.is_strokes_tab_active(), "Strokes tab should be active"


@then("the Ideas tab should be active")
def ideas_tab_active(nav_page: NavigationPage) -> None:
    """Verify Ideas tab is marked active."""
    assert nav_page.is_ideas_tab_active(), "Ideas tab should be active"


@then("the Profile tab should be active")
def profile_tab_active(nav_page: NavigationPage) -> None:
    """Verify Profile tab is marked active."""
    assert nav_page.is_profile_tab_active(), "Profile tab should be active"


@then(parsers.parse('the URL should contain "{hash_value}"'))
def url_contains_hash(nav_page: NavigationPage, hash_value: str) -> None:
    """Verify URL contains the expected hash."""
    nav_page.page.wait_for_timeout(300)
    current_hash = nav_page.get_current_url_hash()
    assert hash_value in current_hash, (
        f"Expected '{hash_value}' in URL, got '{current_hash}'"
    )


@then("I should see the login screen")
def see_login_screen(nav_page: NavigationPage) -> None:
    """Verify login screen is visible."""
    nav_page.page.wait_for_timeout(500)
    assert nav_page.is_login_screen_visible(), "Login screen should be visible"
