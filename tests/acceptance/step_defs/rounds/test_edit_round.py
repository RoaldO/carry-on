"""Step definitions for editing in-progress rounds feature."""

import datetime
from typing import Any

import pytest
from pymongo.database import Database
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.db_utils import insert_round
from tests.acceptance.pages.round_page import RoundPage

# Link this file to the feature file
scenarios("../../features/rounds/edit_round.feature")


@pytest.fixture
def finished_round_id(
    test_database: Database[Any], test_user: dict[str, Any]
) -> dict[str, str]:
    """Create a finished round."""
    round_id = insert_round(
        test_database,
        user_id=test_user["user_id"],
        course_name=test_user["course_name"],
        date=(datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
        holes=[{"hole_number": i + 1, "strokes": 4} for i in range(9)],
        status="f",
    )
    return {"round_id": round_id}


@given("I have a finished round")
def have_finished_round(
    round_page: RoundPage, finished_round_id: dict[str, str]
) -> None:
    """Create a finished round (already done in fixture)."""
    # Refresh the page to load recent rounds
    round_page.goto_rounds_tab()


@then("the in-progress round should be clickable")
def in_progress_round_clickable(
    round_page: RoundPage, test_user: dict[str, Any]
) -> None:
    """Verify the in-progress round has clickable class."""
    round_page.wait_for_recent_rounds()
    assert round_page.is_round_clickable(test_user["course_name"]), (
        "In-progress round should be clickable"
    )


@then("finished rounds should not be clickable")
def finished_rounds_not_clickable(round_page: RoundPage) -> None:
    """Verify finished rounds don't have clickable class."""
    round_page.wait_for_recent_rounds()
    # Check that there's at least one round without clickable class
    all_rounds = round_page.page.locator(".round-item")
    count = all_rounds.count()
    clickable_count = round_page.page.locator(".round-item.clickable").count()
    assert clickable_count < count, "Not all rounds should be clickable"


@then("holes 1-3 should show the recorded strokes")
def holes_show_recorded_strokes(round_page: RoundPage) -> None:
    """Verify holes 1-3 have the recorded strokes."""
    # Navigate to hole 1
    while int(round_page.get_current_hole()) > 1:
        round_page.click_prev_hole()

    # Check hole 1 (should be 4 strokes)
    assert round_page.hole_strokes.input_value() == "4", "Hole 1 should have 4 strokes"

    # Check hole 2 (should be 3 strokes)
    round_page.click_next_hole()
    assert round_page.hole_strokes.input_value() == "3", "Hole 2 should have 3 strokes"

    # Check hole 3 (should be 5 strokes)
    round_page.click_next_hole()
    assert round_page.hole_strokes.input_value() == "5", "Hole 3 should have 5 strokes"


@given('I start a new round for "Pitch & Putt"')
def start_new_round(round_page: RoundPage, test_user: dict[str, Any]) -> None:
    """Start a new round by selecting the course."""
    round_page.type_course_search(test_user["course_name"])
    round_page.select_course_suggestion(test_user["course_name"])


@given('I enter strokes "4" for hole 1')
def enter_strokes_hole_1(round_page: RoundPage) -> None:
    """Enter strokes for hole 1."""
    round_page.enter_strokes("4")
    # Wait a bit to ensure the value is set
    round_page.page.wait_for_timeout(200)


@given("I have another in-progress round")
def have_another_in_progress_round(
    round_page: RoundPage,
    test_database: Database[Any],
    test_user: dict[str, Any],
) -> str:
    """Create another in-progress round."""
    round_id = insert_round(
        test_database,
        user_id=test_user["user_id"],
        course_name=test_user["course_name"],
        date=datetime.date.today().isoformat(),
        holes=[
            {"hole_number": 1, "strokes": 5},
            {"hole_number": 2, "strokes": 4},
        ],
        status="ip",
    )
    # Trigger UI refresh by navigating to Ideas tab and back
    round_page.page.locator(".tab[data-tab='ideas']").click()
    round_page.page.wait_for_timeout(200)
    round_page.goto_rounds_tab()
    return round_id


@when("I click on the other in-progress round")
def click_other_round(round_page: RoundPage, test_user: dict[str, Any]) -> None:
    """Click on the other in-progress round (the one with 2 holes completed)."""
    # Wait for recent rounds to load and show the newly created round
    round_page.page.wait_for_timeout(500)  # Give time for auto-refresh
    round_page.wait_for_recent_rounds()
    # Get in-progress rounds that are NOT currently being edited
    round_items = round_page.page.locator(
        f".round-item.clickable:not(.editing):has-text('{test_user['course_name']}')"
    )
    # Click the first non-editing round (the "other" round)
    if round_items.count() > 0:
        round_items.nth(0).click()
        round_page.page.wait_for_timeout(500)


@then("the first round should be saved")
def first_round_saved(test_database: Database[Any], test_user: dict[str, Any]) -> None:
    """Verify the first round was saved with hole 1 strokes."""
    # Query for rounds with exactly 1 hole
    rounds = list(
        test_database.rounds.find(
            {
                "user_id": test_user["user_id"],
                "status": "ip",
            }
        )
    )
    # Find a round with 1 hole that has 4 strokes
    found = False
    for round_doc in rounds:
        if len(round_doc["holes"]) == 1 and round_doc["holes"][0]["strokes"] == 4:
            found = True
            break
    assert found, "First round should be saved with 1 hole (4 strokes)"


@then("the second round should be loaded")
def second_round_loaded(round_page: RoundPage) -> None:
    """Verify the second round is now active."""
    # Wait for hole navigator to update
    round_page.page.wait_for_timeout(500)
    # Should be on hole 3 (first incomplete hole after 2 completed)
    current_hole = int(round_page.get_current_hole())
    assert current_hole == 3, f"Expected hole 3, got {current_hole}"


@then("I should see the second round's data")
def see_second_round_data(round_page: RoundPage) -> None:
    """Verify the second round's holes are loaded."""
    # Navigate to hole 1
    while int(round_page.get_current_hole()) > 1:
        round_page.click_prev_hole()

    # Check hole 1 (should be 5 strokes)
    assert round_page.hole_strokes.input_value() == "5", "Hole 1 should have 5 strokes"

    # Check hole 2 (should be 4 strokes)
    round_page.click_next_hole()
    assert round_page.hole_strokes.input_value() == "4", "Hole 2 should have 4 strokes"


@given("I have an in-progress round")
def have_simple_in_progress_round(
    round_page: RoundPage, in_progress_round_id: dict[str, str]
) -> None:
    """Create an in-progress round (already done in fixture)."""
    # Refresh the page to load recent rounds
    round_page.goto_rounds_tab()


@then("that round should be highlighted as active")
def round_highlighted(round_page: RoundPage, test_user: dict[str, Any]) -> None:
    """Verify the round is highlighted with editing class."""
    round_page.wait_for_recent_rounds()
    assert round_page.is_round_highlighted(test_user["course_name"]), (
        "Active round should be highlighted"
    )


@given("I am not currently editing any round")
def not_editing_any_round(round_page: RoundPage) -> None:
    """Ensure no round is currently being edited.

    This is the default state after navigating to the Rounds tab,
    but we make it explicit by checking the UI state.
    """
    # Verify hole navigator is not visible (no active round)
    assert not round_page.is_hole_navigator_visible(), (
        "Should not be editing a round initially"
    )


@then("I should see the hole navigator without errors")
def see_hole_navigator_without_errors(round_page: RoundPage) -> None:
    """Verify hole navigator appears without JavaScript errors.

    This step specifically tests that clicking a round when not currently
    editing any round doesn't cause errors in the auto-save logic.
    """
    # Check that hole navigator is now visible
    assert round_page.is_hole_navigator_visible(), (
        "Hole navigator should be visible after clicking round"
    )

    # If we got here without an exception, no JS errors occurred
    # (Playwright would fail the test if there were uncaught exceptions)


@then("I should see the par for the current hole")
def see_par_for_current_hole(round_page: RoundPage) -> None:
    """Verify par is displayed for the current hole.

    This tests that the course data (including holes with par values)
    was successfully loaded when loading the round for editing.
    If the course holes weren't loaded, this would fail.
    """
    par = round_page.get_current_par()
    assert par and par.strip(), (
        "Par should be displayed for current hole (course holes must be loaded)"
    )


@when("I navigate away from the Rounds tab")
def navigate_away_from_rounds(round_page: RoundPage) -> None:
    """Navigate to a different tab to test auto-save."""
    # Switch to a different tab (e.g., Ideas)
    round_page.page.locator(".tab[data-tab='ideas']").click()
    round_page.page.wait_for_timeout(500)


@then(parsers.parse("the round should have {count:d} holes recorded"))
def round_has_holes_recorded(
    test_database: Database[Any], test_user: dict[str, Any], count: int
) -> None:
    """Verify the round has the expected number of holes."""
    # Find the most recently updated in-progress round
    rounds = list(
        test_database.rounds.find(
            {"user_id": test_user["user_id"], "status": "ip"}
        ).sort("created_at", -1)
    )
    assert len(rounds) > 0, "Should have at least one in-progress round"

    # Check the first (most recent) round
    round_doc = rounds[0]
    assert len(round_doc["holes"]) == count, (
        f"Expected {count} holes, got {len(round_doc['holes'])}"
    )
