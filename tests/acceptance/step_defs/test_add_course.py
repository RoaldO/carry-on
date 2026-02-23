"""Step definitions for adding a golf course feature."""

from typing import Any

import pytest
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import hash_password
from tests.acceptance.db_utils import insert_user
from tests.acceptance.pages.course_page import CoursePage
from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/courses/add_course.feature")


@pytest.fixture
def course_page(page: Page, base_url: str) -> CoursePage:
    """Create a CoursePage instance for the test."""
    return CoursePage(page, base_url)


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


@given("I navigate to the courses page")
def navigate_to_courses(course_page: CoursePage) -> None:
    """Navigate to the courses page."""
    course_page.navigate_to_courses()


@when("I click the add course button")
def click_add_course(course_page: CoursePage) -> None:
    """Click the Add Course button."""
    course_page.click_add_course()


@when(parsers.parse('I enter course name "{name}"'))
def enter_course_name(course_page: CoursePage, name: str) -> None:
    """Enter a course name."""
    course_page.enter_course_name(name)


@when(parsers.parse("I select {count:d} holes"))
def select_holes(course_page: CoursePage, count: int) -> None:
    """Select number of holes."""
    course_page.select_hole_count(count)


@when(parsers.parse("I fill in the hole details for {count:d} holes"))
def fill_hole_details(course_page: CoursePage, count: int) -> None:
    """Fill in the hole details."""
    course_page.fill_hole_details(count)


@when("I submit the course form")
def submit_course_form(course_page: CoursePage) -> None:
    """Submit the course form."""
    course_page.submit_course_form()


@when("I reload the courses page")
def reload_courses_page(course_page: CoursePage) -> None:
    """Reload the page and navigate back to courses."""
    course_page.reload()


@then(parsers.parse('I should see "{name}" in the course list'))
def should_see_course(course_page: CoursePage, name: str) -> None:
    """Verify a course is visible in the course list."""
    course_page.wait_for_course_in_list(name)
    assert course_page.is_course_in_list(name), f"Expected '{name}' in the course list"


@when(parsers.parse('I enter slope rating "{value}"'))
def enter_slope_rating(course_page: CoursePage, value: str) -> None:
    """Enter a slope rating."""
    course_page.enter_slope_rating(value)


@when(parsers.parse('I enter course rating "{value}"'))
def enter_course_rating(course_page: CoursePage, value: str) -> None:
    """Enter a course rating."""
    course_page.enter_course_rating(value)


@then(parsers.parse('"{name}" should show slope rating "{value}"'))
def should_show_slope_rating(course_page: CoursePage, name: str, value: str) -> None:
    """Verify a course displays the expected slope rating."""
    actual = course_page.get_course_slope_rating(name)
    assert actual == value, (
        f"Expected slope rating '{value}' for '{name}', got '{actual}'"
    )


@then(parsers.parse('"{name}" should show course rating "{value}"'))
def should_show_course_rating(course_page: CoursePage, name: str, value: str) -> None:
    """Verify a course displays the expected course rating."""
    actual = course_page.get_course_course_rating(name)
    assert actual == value, (
        f"Expected course rating '{value}' for '{name}', got '{actual}'"
    )


@then("I should see a course form error")
def should_see_form_error(course_page: CoursePage) -> None:
    """Verify a form error is shown."""
    course_page.wait_for_form_error()
    assert course_page.has_form_error(), "Expected a course form error"
