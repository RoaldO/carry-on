import os
import socket
import threading
import time
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import uvicorn
from playwright.sync_api import Page
from pytest_bdd import given, parsers, then, when

from carry_on.api.pin_security import hash_pin
from tests.acceptance.pages.login_page import LoginPage
from tests.acceptance.pages.stroke_page import StrokePage

pytestmark = pytest.mark.acceptance


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class ServerThread(threading.Thread):
    def __init__(self, app: Any, host: str, port: int) -> None:
        super().__init__(daemon=True)
        self.app = app
        self.host = host
        self.port = port
        self.server: uvicorn.Server | None = None

    def run(self) -> None:
        config = uvicorn.Config(
            self.app, host=self.host, port=self.port, log_level="warning"
        )
        self.server = uvicorn.Server(config)
        self.server.run()

    def stop(self) -> None:
        if self.server:
            self.server.should_exit = True


@pytest.fixture(scope="session")
def mock_collections() -> dict[str, MagicMock]:
    return {
        "users": MagicMock(),
        "strokes": MagicMock(),
        "ideas": MagicMock(),
    }


@pytest.fixture(scope="session")
def app_port() -> int:
    return find_free_port()


@pytest.fixture(scope="session")
def base_url(app_port: int) -> str:
    return f"http://localhost:{app_port}"


@pytest.fixture(scope="session")
def app_server(
    mock_collections: dict[str, MagicMock], app_port: int
) -> Generator[ServerThread, None, None]:
    os.environ["MONGODB_URI"] = "mongodb://test"

    with (
        patch(
            "carry_on.api.index.get_users_collection",
            return_value=mock_collections["users"],
        ),
        patch(
            "carry_on.api.strokes.get_strokes_collection",
            return_value=mock_collections["strokes"],
        ),
        patch(
            "carry_on.api.ideas.get_ideas_collection",
            return_value=mock_collections["ideas"],
        ),
    ):
        from carry_on.api.index import app

        server = ServerThread(app, "127.0.0.1", app_port)
        server.start()

        # Wait for server to be ready
        time.sleep(0.5)

        yield server

        server.stop()

    os.environ.pop("MONGODB_URI", None)


@pytest.fixture
def page(
    browser: Any, base_url: str, app_server: ServerThread
) -> Generator[Page, None, None]:
    context = browser.new_context(viewport={"width": 400, "height": 800})
    page = context.new_page()
    page.goto(base_url)
    yield page
    context.close()


@pytest.fixture
def inactive_user(mock_collections: dict[str, MagicMock]) -> dict[str, Any]:
    """Create an inactive user (needs activation) in the mock database."""
    user = {
        "_id": "inactive_user_123",
        "email": "inactive@example.com",
        "display_name": "Inactive User",
        "pin_hash": None,
        "activated_at": None,
    }

    def find_one(query: dict) -> dict | None:
        if query.get("email") == user["email"]:
            return user
        return None

    mock_collections["users"].find_one.side_effect = find_one
    return user


@pytest.fixture
def activated_user_email() -> str:
    return "active@test.com"


@pytest.fixture
def activated_user_pin() -> str:
    return "1234"


@pytest.fixture
def activated_user(
    mock_collections: dict[str, MagicMock],
    activated_user_email: str,
    activated_user_pin: str,
) -> dict[str, Any]:
    """Create an activated user in the mock database."""
    user = {
        "_id": "activated_user_456",
        "email": activated_user_email,
        "display_name": "Active User",
        "pin_hash": hash_pin(activated_user_pin),
        "activated_at": "2026-01-25T10:00:00Z",
    }

    def find_one(query: dict) -> dict | None:
        if query.get("email") == user["email"]:
            return user
        return None

    mock_collections["users"].find_one.side_effect = find_one
    return {**user, "pin": activated_user_pin}  # Include plain PIN for test use


@pytest.fixture
def clear_mock_users(
    mock_collections: dict[str, MagicMock],
) -> Generator[None, None, None]:
    yield
    mock_collections["users"].reset_mock()
    mock_collections["users"].find_one.side_effect = None
    mock_collections["users"].find_one.return_value = None


@pytest.fixture
def login_page(page: Page, base_url: str) -> LoginPage:
    return LoginPage(page, base_url)


@pytest.fixture
def stroke_page(page: Page, base_url: str) -> StrokePage:
    return StrokePage(page, base_url)


# Shared step definitions
@given("I am on the login screen")
def on_login_screen(login_page: LoginPage) -> None:
    login_page.goto_login()


@when(parsers.parse('I enter email "{email}"'))
def enter_email(login_page: LoginPage, email: str) -> None:
    login_page.enter_email(email)


@when("I click the continue button")
def click_continue(login_page: LoginPage) -> None:
    login_page.click_continue()


@when(parsers.parse('I enter PIN "{pin}"'))
def enter_pin(login_page: LoginPage, pin: str) -> None:
    login_page.enter_pin(pin)


@when(parsers.parse('I enter confirm PIN "{pin}"'))
def enter_confirm_pin(login_page: LoginPage, pin: str) -> None:
    login_page.enter_confirm_pin(pin)


@when("I click the submit button")
def click_submit(login_page: LoginPage) -> None:
    login_page.click_submit()


@then("I should be logged in")
def should_be_logged_in(login_page: LoginPage) -> None:
    login_page.wait_for_logged_in()
    assert login_page.is_login_screen_hidden(), "Login screen should be hidden"


@then("the tab bar should be visible")
def tab_bar_visible(login_page: LoginPage) -> None:
    assert login_page.is_tab_bar_visible(), "Tab bar should be visible"


@then(parsers.parse('I should see PIN error "{error}"'))
def see_pin_error(login_page: LoginPage, error: str) -> None:
    login_page.wait_for_pin_error()
    actual_error = login_page.get_pin_error()
    assert error in actual_error, f"Expected '{error}' in '{actual_error}'"


@then(parsers.parse('I should see email error "{error}"'))
def see_email_error(login_page: LoginPage, error: str) -> None:
    login_page.wait_for_email_error()
    actual_error = login_page.get_email_error()
    assert error in actual_error, f"Expected '{error}' in '{actual_error}'"


@then(parsers.parse('I should see "{text}"'))
def see_text(login_page: LoginPage, text: str) -> None:
    welcome_text = login_page.get_welcome_name()
    assert text in welcome_text, f"Expected '{text}' in '{welcome_text}'"


@given("an authenticated user")
def an_authenticated_user(
    login_page: LoginPage,
    activated_user_email: str,
    activated_user_pin: str,
    activated_user: dict[str, Any],
):
    login_page.goto_login()
    login_page.enter_email(activated_user_email)
    login_page.click_continue()
    login_page.wait_for_pin_step()
    login_page.enter_pin(activated_user_pin)
    login_page.click_submit()
    login_page.wait_for_logged_in()
