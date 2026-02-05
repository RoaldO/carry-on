"""Step definitions for stroke recording feature."""

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.pages.stroke_page import StrokePage


scenarios("../../features/strokes/record.feature")


@when(parsers.parse("the user records a stroke with distance {distance:d}"))
def record_stroke_with_distance(stroke_page: StrokePage, distance: int) -> None:
    stroke_page.record_stroke(distance)


@when("the user records a stroke")
def the_user_records_a_stroke(stroke_page: StrokePage) -> None:
    stroke_page.record_stroke()


@when("the user records a failed stroke")
def record_failed_stroke(stroke_page: StrokePage) -> None:
    stroke_page.record_failed_stroke()


@when("the user submits a stroke without distance or fail")
def submit_without_distance_or_fail(stroke_page: StrokePage) -> None:
    stroke_page.submit_without_distance_or_fail()


@when("the user views recent strokes")
def view_recent_strokes(stroke_page: StrokePage) -> None:
    stroke_page.wait_for_recent_strokes()


@given("the user has recorded strokes")
def user_has_recorded_strokes(stroke_page: StrokePage) -> None:
    # Record a couple of strokes to have data
    stroke_page.record_stroke(120)
    stroke_page.get_message()  # Wait for first to complete
    stroke_page.record_stroke(145)
    stroke_page.get_message()  # Wait for second to complete


@then("the stroke is confirmed")
def the_stroke_is_confirmed(stroke_page: StrokePage) -> None:
    assert "Recorded:" in stroke_page.get_message()


@then(parsers.parse("the stroke is confirmed with distance {distance:d}"))
def stroke_confirmed_with_distance(stroke_page: StrokePage, distance: int) -> None:
    message = stroke_page.get_message()
    assert "Recorded:" in message
    assert f"{distance}m" in message


@then("the stroke is confirmed as failed")
def stroke_confirmed_as_failed(stroke_page: StrokePage) -> None:
    message = stroke_page.get_message()
    assert "Recorded:" in message
    assert "FAIL" in message


@then("the recent strokes are displayed")
def recent_strokes_displayed(stroke_page: StrokePage) -> None:
    stroke_page.wait_for_recent_strokes()
    assert stroke_page.has_stroke_items()


@then("an error message is shown")
def error_message_shown(stroke_page: StrokePage) -> None:
    message = stroke_page.get_message()
    assert "error" in message.lower() or "distance" in message.lower()
