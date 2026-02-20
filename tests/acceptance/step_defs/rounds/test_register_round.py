"""Step definitions for round registration feature."""

import datetime
from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.pages.round_page import RoundPage

# Link this file to the feature file
scenarios("../../features/rounds/register_round.feature")


@then("I should see the round date input with today's date")
def see_date_with_today(round_page: RoundPage) -> None:
    """Verify date input shows today's date."""
    today = datetime.date.today().isoformat()
    actual = round_page.get_date_value()
    assert actual == today, f"Expected date '{today}', got '{actual}'"


@then(parsers.parse('I should see "{name}" in the course suggestions'))
def see_course_suggestion(round_page: RoundPage, name: str) -> None:
    """Verify a course appears in the suggestions."""
    suggestions = round_page.get_suggestions()
    assert any(name in s for s in suggestions), (
        f"Expected '{name}' in suggestions: {suggestions}"
    )


@then(parsers.parse("I should see the par for hole {number:d}"))
def see_par_for_hole(round_page: RoundPage, number: int) -> None:
    """Verify par is displayed for the given hole."""
    par = round_page.get_current_par()
    assert par, f"Expected par to be displayed for hole {number}"


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
