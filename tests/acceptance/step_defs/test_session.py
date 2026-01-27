"""Step definitions for session persistence feature."""

from typing import Any
from unittest.mock import MagicMock

from pytest_bdd import given, parsers, scenarios, then, when

from api.pin_security import hash_pin
from tests.acceptance.pages.login_page import LoginPage

# Link this file to the feature file
scenarios("../features/auth/session.feature")


@given(
    parsers.parse('a user exists with email "{email}" and PIN "{pin}"'),
    target_fixture="test_user",
)
def user_with_pin(
    mock_collections: dict[str, MagicMock], email: str, pin: str
) -> dict[str, Any]:
    """Create an activated user with a PIN in the mock database."""
    user = {
        "_id": f"user_{email.replace('@', '_').replace('.', '_')}",
        "email": email,
        "display_name": "Session Test User",
        "pin_hash": hash_pin(pin),
        "activated_at": "2026-01-25T10:00:00Z",
    }

    original_side_effect = mock_collections["users"].find_one.side_effect

    def find_one(query: dict) -> dict | None:
        if query.get("email") == email:
            return user
        if original_side_effect:
            return original_side_effect(query)
        return None

    mock_collections["users"].find_one.side_effect = find_one

    # Also set up the strokes collection to return empty for this user
    mock_collections[
        "strokes"
    ].find.return_value.sort.return_value.limit.return_value = []

    return {**user, "pin": pin}


@when(parsers.parse('I log in with email "{email}" and PIN "{pin}"'))
def log_in(login_page: LoginPage, email: str, pin: str) -> None:
    """Perform a complete login flow."""
    login_page.enter_email(email)
    login_page.click_continue()
    login_page.wait_for_pin_step()
    login_page.enter_pin(pin)
    login_page.click_submit()


@when("I clear local storage")
def clear_local_storage(login_page: LoginPage) -> None:
    """Clear the browser's local storage."""
    login_page.clear_local_storage()


@when("I set invalid credentials in local storage")
def set_invalid_credentials(login_page: LoginPage) -> None:
    """Set invalid credentials in localStorage to simulate corrupted session."""
    login_page.page.evaluate("""
        localStorage.setItem('carryon_email', 'invalid@example.com');
        localStorage.setItem('carryon_pin', 'wrongpin');
    """)


@when("I click the Ideas tab")
def click_ideas_tab(login_page: LoginPage) -> None:
    """Click on the Ideas tab."""
    login_page.page.locator(".tab[data-tab='ideas']").click()


@when("I click the Strokes tab")
def click_strokes_tab(login_page: LoginPage) -> None:
    """Click on the Strokes tab."""
    login_page.page.locator(".tab[data-tab='strokes']").click()


@when("I reload the page")
def reload_page(login_page: LoginPage) -> None:
    """Reload the current page."""
    login_page.reload()


@then("I should still be logged in")
def still_logged_in(login_page: LoginPage) -> None:
    """Verify user is still logged in after action."""
    # Wait a moment for the page to check localStorage and auto-login
    login_page.page.wait_for_timeout(1000)
    assert login_page.is_login_screen_hidden(), "Should still be logged in"


@then("I should see the login screen")
def see_login_screen(login_page: LoginPage) -> None:
    """Verify the login screen is visible."""
    login_page.login_screen.wait_for(state="visible")
    assert login_page.is_login_screen_visible(), "Login screen should be visible"


@then("I should be able to view my strokes")
def can_view_strokes(login_page: LoginPage) -> None:
    """Verify the user can access the strokes view (API works with session)."""
    # The strokes tab should be visible and accessible
    strokes_content = login_page.page.locator("#strokesContent")
    assert strokes_content.is_visible(), "Strokes content should be visible"
    # Check that recent strokes section exists (proves API call succeeded)
    recent_strokes = login_page.page.locator("#recentStrokes")
    assert recent_strokes.is_visible(), "Recent strokes section should be visible"


@then("I should be on the Ideas tab")
def on_ideas_tab(login_page: LoginPage) -> None:
    """Verify the Ideas tab is active."""
    ideas_tab = login_page.page.locator(".tab[data-tab='ideas']")
    classes = ideas_tab.get_attribute("class") or ""
    assert "active" in classes, "Ideas tab should be active"

    ideas_content = login_page.page.locator("#ideasContent")
    assert ideas_content.is_visible(), "Ideas content should be visible"


@then("I should be on the Strokes tab")
def on_strokes_tab(login_page: LoginPage) -> None:
    """Verify the Strokes tab is active."""
    strokes_tab = login_page.page.locator(".tab[data-tab='strokes']")
    classes = strokes_tab.get_attribute("class") or ""
    assert "active" in classes, "Strokes tab should be active"

    strokes_content = login_page.page.locator("#strokesContent")
    assert strokes_content.is_visible(), "Strokes content should be visible"
