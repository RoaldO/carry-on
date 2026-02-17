"""Shared step definitions and fixtures for round tests."""

from typing import Any

import pytest
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, then, when

from tests.acceptance.conftest import hash_password
from tests.acceptance.db_utils import insert_course, insert_user
from tests.acceptance.pages.login_page import LoginPage
from tests.acceptance.pages.round_page import RoundPage


def _make_9_holes() -> list[dict[str, int]]:
    """Create 9 hole definitions with standard pars."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4]
    return [
        {"hole_number": i + 1, "par": pars[i], "stroke_index": i + 1} for i in range(9)
    ]


@pytest.fixture
def round_page(page: Page, base_url: str) -> RoundPage:
    """Create a RoundPage instance for the test."""
    return RoundPage(page, base_url)


@given(
    parsers.parse('a user with a {count:d}-hole course "{course_name}"'),
    target_fixture="test_user",
)
def user_with_course(
    test_database: Database[Any], count: int, course_name: str
) -> dict[str, Any]:
    """Create a user with a course in the database."""
    password = "Password5678!"  # pragma: allowlist secret
    password_hash = hash_password(password)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email="rounds@example.com",
        display_name="Rounds User",
        password_hash=password_hash,
        activated_at=activated_at,
    )
    course_id = insert_course(
        test_database,
        user_id=user_id,
        name=course_name,
        holes=_make_9_holes()[:count],
    )
    return {
        "user_id": user_id,
        "email": "rounds@example.com",
        "password": password,
        "course_id": course_id,
        "course_name": course_name,
    }


@given("I am logged in and on the Rounds tab")
def logged_in_on_rounds(
    login_page: LoginPage,
    round_page: RoundPage,
    test_user: dict[str, Any],
) -> None:
    """Log in and navigate to the Rounds tab."""
    login_page.goto_login()
    login_page.enter_email(test_user["email"])
    login_page.click_continue()
    login_page.wait_for_pin_step()
    login_page.enter_pin(test_user["password"])
    login_page.click_submit()
    login_page.wait_for_logged_in()
    round_page.goto_rounds_tab()


@when("I view the recent rounds section")
def view_recent_rounds(round_page: RoundPage) -> None:
    """Wait for recent rounds to load."""
    round_page.wait_for_recent_rounds()


@then("I should see the hole navigator")
def see_hole_navigator(round_page: RoundPage) -> None:
    """Verify the hole navigator is visible."""
    assert round_page.is_hole_navigator_visible(), "Hole navigator should be visible"


@then(parsers.parse("the current hole should be {number:d}"))
def current_hole_is(round_page: RoundPage, number: int) -> None:
    """Verify the current hole number."""
    actual = round_page.get_current_hole()
    assert str(number) in actual, f"Expected hole {number}, got '{actual}'"


@when(parsers.parse('I enter strokes "{strokes}" for the current hole'))
def enter_strokes(round_page: RoundPage, strokes: str) -> None:
    """Enter strokes for the current hole."""
    round_page.enter_strokes(strokes)
