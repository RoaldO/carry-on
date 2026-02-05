"""Step definitions for idea submission feature."""

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.pages.ideas_page import IdeasPage


scenarios("../../features/ideas/submit.feature")


@given("the user is on the Ideas tab")
def user_on_ideas_tab(ideas_page: IdeasPage) -> None:
    ideas_page.goto_ideas_tab()


@when(parsers.parse('the user submits an idea "{description}"'))
def submit_idea(ideas_page: IdeasPage, description: str) -> None:
    ideas_page.submit_idea(description)


@when("the user tries to submit an empty idea")
def try_submit_empty_idea(ideas_page: IdeasPage) -> None:
    ideas_page.try_submit_empty()


@when(parsers.parse("the user types an idea with {count:d} characters"))
def type_idea_with_chars(ideas_page: IdeasPage, count: int) -> None:
    # Generate a string of exactly the specified length
    text = "x" * count
    ideas_page.type_idea(text)


@then("the idea submission is confirmed")
def idea_confirmed(ideas_page: IdeasPage) -> None:
    message = ideas_page.get_message()
    assert "submitted" in message.lower() or "thank you" in message.lower()


@then("the form is not submitted")
def form_not_submitted(ideas_page: IdeasPage) -> None:
    # HTML5 validation prevents submission of empty required fields
    assert not ideas_page.is_form_valid()


@then(parsers.parse("the character counter shows {remaining:d} remaining"))
def check_char_counter(ideas_page: IdeasPage, remaining: int) -> None:
    assert ideas_page.get_char_count() == remaining
