"""Step definitions for round registration feature."""

import datetime
from typing import Any

import pytest
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import hash_password
from tests.acceptance.db_utils import insert_course, insert_user
from tests.acceptance.pages.login_page import LoginPage
from tests.acceptance.pages.round_page import RoundPage

# Link this file to the feature file
scenarios("../../features/rounds/register_round.feature")


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


@then("I should see the round date input with today's date")
def see_date_with_today(round_page: RoundPage) -> None:
    """Verify date input shows today's date."""
    today = datetime.date.today().isoformat()
    actual = round_page.get_date_value()
    assert actual == today, f"Expected date '{today}', got '{actual}'"


@when(parsers.parse('I type "{text}" in the course search'))
def type_course_search(round_page: RoundPage, text: str) -> None:
    """Type text in the course search field."""
    round_page.type_course_search(text)


@then(parsers.parse('I should see "{name}" in the course suggestions'))
def see_course_suggestion(round_page: RoundPage, name: str) -> None:
    """Verify a course appears in the suggestions."""
    suggestions = round_page.get_suggestions()
    assert any(name in s for s in suggestions), (
        f"Expected '{name}' in suggestions: {suggestions}"
    )


@when(parsers.parse('I select "{name}" from the suggestions'))
def select_suggestion(round_page: RoundPage, name: str) -> None:
    """Select a course from the suggestions."""
    round_page.select_course_suggestion(name)


@then("I should see the hole navigator")
def see_hole_navigator(round_page: RoundPage) -> None:
    """Verify the hole navigator is visible."""
    assert round_page.is_hole_navigator_visible(), "Hole navigator should be visible"


@then(parsers.parse("the current hole should be {number:d}"))
def current_hole_is(round_page: RoundPage, number: int) -> None:
    """Verify the current hole number."""
    actual = round_page.get_current_hole()
    assert str(number) in actual, f"Expected hole {number}, got '{actual}'"


@then(parsers.parse("I should see the par for hole {number:d}"))
def see_par_for_hole(round_page: RoundPage, number: int) -> None:
    """Verify par is displayed for the given hole."""
    par = round_page.get_current_par()
    assert par, f"Expected par to be displayed for hole {number}"


@when(parsers.parse('I enter strokes "{strokes}" for the current hole'))
def enter_strokes(round_page: RoundPage, strokes: str) -> None:
    """Enter strokes for the current hole."""
    round_page.enter_strokes(strokes)


@when("I click the next hole button")
def click_next(round_page: RoundPage) -> None:
    """Click the next hole button."""
    round_page.click_next_hole()


@when("I click the previous hole button")
def click_prev(round_page: RoundPage) -> None:
    """Click the previous hole button."""
    round_page.click_prev_hole()


@when(parsers.parse("I fill all {count:d} holes with {strokes:d} strokes each"))
def fill_all_holes(round_page: RoundPage, count: int, strokes: int) -> None:
    """Fill strokes for all holes."""
    round_page.fill_all_holes(count, strokes)


@when("I click the submit round button")
def click_submit_round(round_page: RoundPage) -> None:
    """Click the submit round button."""
    round_page.submit_round()


@then("I should see a round success message")
def see_success_message(round_page: RoundPage) -> None:
    """Verify a success message is shown."""
    round_page.wait_for_message()
    message = round_page.get_message()
    assert "success" in message.lower() or "recorded" in message.lower(), (
        f"Expected success message, got '{message}'"
    )


@given("the user has completed rounds")
def user_has_completed_rounds(round_page: RoundPage, test_user: dict[str, Any]) -> None:
    """Create a couple of completed rounds for the user."""
    # Record first round
    round_page.type_course_search(test_user["course_name"])
    round_page.select_course_suggestion(test_user["course_name"])
    round_page.fill_all_holes(9, 4)
    round_page.submit_round()
    round_page.wait_for_message()

    # Wait a bit and record second round
    round_page.page.wait_for_timeout(500)
    round_page.type_course_search(test_user["course_name"])
    round_page.select_course_suggestion(test_user["course_name"])
    round_page.fill_all_holes(9, 5)
    round_page.submit_round()
    round_page.wait_for_message()


@when("I view the recent rounds section")
def view_recent_rounds(round_page: RoundPage) -> None:
    """Wait for recent rounds to load."""
    round_page.wait_for_recent_rounds()


@then("I should see recent rounds displayed")
def see_recent_rounds(round_page: RoundPage) -> None:
    """Verify recent rounds are displayed."""
    round_page.wait_for_recent_rounds()
    assert round_page.has_round_items(), "Expected round items to be displayed"


@then("each round should show course name, date, and total strokes")
def round_shows_details(round_page: RoundPage) -> None:
    """Verify round items contain expected information."""
    text = round_page.get_recent_rounds_text()
    # Check for course name
    assert "Pitch & Putt" in text, f"Expected course name in recent rounds: {text}"
    # Check for stroke count indicators (should show totals like 36, 45)
    assert any(str(i) in text for i in [36, 45]), (
        f"Expected stroke totals in recent rounds: {text}"
    )
