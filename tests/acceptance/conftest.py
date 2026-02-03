import socket
import threading
import time
from collections.abc import Generator
from typing import Any

import pytest
import uvicorn
from playwright.sync_api import Page
from pymongo.database import Database
from pytest_bdd import given, parsers, then, when

from carry_on.api.password_security import hash_password
from tests.acceptance.db_utils import clear_collections, get_test_database, insert_user
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
def test_database() -> Database[Any]:
    """Get MongoDB database connection for tests."""
    return get_test_database()


@pytest.fixture(autouse=True)
def clean_database(test_database: Database[Any]) -> Generator[None, None, None]:
    """Clear all test collections before each test."""
    clear_collections(test_database)
    yield


@pytest.fixture(scope="session")
def app_port() -> int:
    return find_free_port()


@pytest.fixture(scope="session")
def base_url(app_port: int) -> str:
    return f"http://localhost:{app_port}"


@pytest.fixture(scope="session")
def app_server(app_port: int) -> Generator[ServerThread, None, None]:
    from carry_on.api.index import app

    server = ServerThread(app, "127.0.0.1", app_port)
    server.start()

    # Wait for server to be ready
    time.sleep(0.5)

    yield server

    server.stop()


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
def inactive_user(test_database: Database[Any]) -> dict[str, Any]:
    """Create an inactive user (needs activation) in the database."""
    email = "inactive@example.com"
    user_id = insert_user(
        test_database,
        email=email,
        display_name="Inactive User",
        password_hash=None,
        activated_at=None,
    )
    return {
        "_id": user_id,
        "email": email,
        "display_name": "Inactive User",
        "password_hash": None,
        "activated_at": None,
    }


@pytest.fixture
def activated_user_email() -> str:
    return "active@test.com"


@pytest.fixture
def activated_user_password() -> str:
    return "1234"


@pytest.fixture
def activated_user(
    test_database: Database[Any],
    activated_user_email: str,
    activated_user_password: str,
) -> dict[str, Any]:
    """Create an activated user in the database."""
    password_hash = hash_password(activated_user_password)
    activated_at = "2026-01-25T10:00:00Z"
    user_id = insert_user(
        test_database,
        email=activated_user_email,
        display_name="Active User",
        password_hash=password_hash,
        activated_at=activated_at,
    )
    return {
        "_id": user_id,
        "email": activated_user_email,
        "display_name": "Active User",
        "password_hash": password_hash,
        "activated_at": activated_at,
        "password": activated_user_password,  # Include plain password for test use
    }


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


@when(parsers.parse('I enter password "{password}"'))
def enter_password(login_page: LoginPage, password: str) -> None:
    login_page.enter_pin(password)


@when(parsers.parse('I enter confirm password "{password}"'))
def enter_confirm_password(login_page: LoginPage, password: str) -> None:
    login_page.enter_confirm_pin(password)


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


@then(parsers.parse('I should see password error "{error}"'))
def see_password_error(login_page: LoginPage, error: str) -> None:
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
    activated_user_password: str,
    activated_user: dict[str, Any],
):
    login_page.goto_login()
    login_page.enter_email(activated_user_email)
    login_page.click_continue()
    login_page.wait_for_pin_step()
    login_page.enter_pin(activated_user_password)
    login_page.click_submit()
    login_page.wait_for_logged_in()
