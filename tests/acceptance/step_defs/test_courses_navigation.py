"""Step definitions for course management navigation feature."""

from typing import Any

import pytest
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import hash_password
from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.login_page import LoginPage
from tests.acceptance.pages.navigation_page import NavigationPage

# Link this file to the feature file
scenarios("../features/navigation/courses.feature")


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
    password_hash = hash_password(password)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email=email,
        display_name=display_name,
        password_hash=password_hash,
        activated_at=activated_at,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": display_name,
        "password_hash": password_hash,
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


@when(parsers.parse('I click the "{link_text}" link'))
def click_named_link(nav_page: NavigationPage, link_text: str) -> None:
    """Click a named link on the page."""
    if link_text == "My Courses":
        nav_page.click_my_courses_link()
    else:
        msg = f"Unknown link: {link_text}"
        raise ValueError(msg)


@when("I click the back link")
def click_back_link(nav_page: NavigationPage) -> None:
    """Click the back link on the courses page."""
    nav_page.click_courses_back_link()


@then(parsers.parse('I should see the "{link_text}" link'))
def should_see_named_link(nav_page: NavigationPage, link_text: str) -> None:
    """Verify a named link is visible."""
    if link_text == "My Courses":
        assert nav_page.is_my_courses_link_visible(), (
            "My Courses link should be visible"
        )
    else:
        msg = f"Unknown link: {link_text}"
        raise ValueError(msg)


@then("I should see the courses page")
def should_see_courses_page(nav_page: NavigationPage) -> None:
    """Verify the courses page content is visible."""
    assert nav_page.is_on_courses_page(), "Courses page should be visible"


@then("the Profile tab should be active")
def profile_tab_should_be_active(nav_page: NavigationPage) -> None:
    """Verify the Profile tab is highlighted as active."""
    assert nav_page.is_profile_tab_active(), "Profile tab should be active"


@then("I should be on the Profile tab")
def should_be_on_profile_tab(nav_page: NavigationPage) -> None:
    """Verify we are on the profile tab."""
    assert nav_page.is_on_profile_tab(), "Should be on the Profile tab"
