"""Step definitions for profile display feature."""

from pytest_bdd import scenarios, then, when

from tests.acceptance.pages.stroke_page import StrokePage


scenarios("../../features/strokes/record.feature")


@when("the user records a stroke")
def the_user_records_a_stroke(
    stroke_page: StrokePage,
):
    stroke_page.record_stroke()


@then("the stroke is confirmed")
def the_stroke_is_confirmed(
    stroke_page: StrokePage,
):
    assert "Recorded:" in stroke_page.get_message()
