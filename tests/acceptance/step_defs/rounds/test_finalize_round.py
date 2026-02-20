"""Step definitions for round finalization feature."""

from pytest_bdd import parsers, scenarios, then, when

from tests.acceptance.pages.round_page import RoundPage

# Link this file to the feature file
scenarios("../../features/rounds/finalize_round.feature")


@then(parsers.parse('I should see the "{button_name}" button'))
def see_button(round_page: RoundPage, button_name: str) -> None:
    """Verify a specific button is visible."""
    if button_name == "Save Progress":
        assert round_page.is_save_progress_visible(), (
            "Save Progress button should be visible"
        )
    elif button_name == "Finish Round":
        assert round_page.is_finish_round_visible(), (
            "Finish Round button should be visible"
        )
    else:
        raise ValueError(f"Unknown button: {button_name}")


@when(parsers.parse('I click the "{button_name}" button'))
def click_button(round_page: RoundPage, button_name: str) -> None:
    """Click a named button."""
    if button_name == "Save Progress":
        round_page.click_save_progress()
    elif button_name == "Finish Round":
        round_page.click_finish_round()
    else:
        raise ValueError(f"Unknown button: {button_name}")


@when(parsers.parse("I fill the remaining holes with {strokes:d} strokes each"))
def fill_remaining_holes(round_page: RoundPage, strokes: int) -> None:
    """Fill all remaining unfilled holes with the given strokes."""
    # We're on the first incomplete hole; fill through to the last hole
    while True:
        round_page.enter_strokes(str(strokes))
        # Try to advance; if we're on the last hole the next button won't advance
        current = round_page.get_current_hole()
        round_page.click_next_hole()
        next_hole = round_page.get_current_hole()
        if next_hole == current:
            # We're on the last hole, done filling
            break


@then("I should see a progress saved message")
def see_progress_saved(round_page: RoundPage) -> None:
    """Verify a progress-saved confirmation message is shown."""
    round_page.wait_for_message()
    message = round_page.get_message().lower()
    assert "progress saved" in message or "saved" in message, (
        f"Expected progress saved message, got '{message}'"
    )


@then("I should see a round finished message")
def see_round_finished(round_page: RoundPage) -> None:
    """Verify a round-finished success message is shown."""
    round_page.wait_for_message()
    message = round_page.get_message().lower()
    assert "finished" in message or "success" in message, (
        f"Expected round finished message, got '{message}'"
    )


@then(parsers.parse('the "{button_name}" button should be disabled'))
def button_disabled(round_page: RoundPage, button_name: str) -> None:
    """Verify a button is disabled."""
    if button_name == "Finish Round":
        assert round_page.is_finish_round_disabled(), (
            "Finish Round button should be disabled"
        )
    else:
        raise ValueError(f"Unknown button: {button_name}")


@then(parsers.parse('the "{button_name}" button should be enabled'))
def button_enabled(round_page: RoundPage, button_name: str) -> None:
    """Verify a button is enabled."""
    if button_name == "Finish Round":
        assert not round_page.is_finish_round_disabled(), (
            "Finish Round button should be enabled"
        )
    else:
        raise ValueError(f"Unknown button: {button_name}")
