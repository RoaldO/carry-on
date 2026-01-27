"""Page Object Model for the login screen."""

from playwright.sync_api import Page, expect


class LoginPage:
    """Page object for the CarryOn login/registration screen."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Login screen container
        self.login_screen = page.locator("#loginScreen")

        # Email step elements
        self.email_input = page.locator("#email")
        self.continue_button = page.locator("#emailForm button[type='submit']")
        self.email_message = page.locator("#emailMessage")

        # PIN step elements
        self.pin_input = page.locator("#pin")
        self.confirm_pin_input = page.locator("#confirmPin")
        self.confirm_pin_group = page.locator("#confirmPinGroup")
        self.pin_label = page.locator("#pinLabel")
        self.submit_button = page.locator("#pinSubmitBtn")
        self.pin_message = page.locator("#pinMessage")
        self.welcome_name = page.locator("#welcomeName")
        self.back_button = page.locator("#backToEmail")

        # Tab bar (visible after login)
        self.tab_bar = page.locator("#tabBar")

    def goto_login(self) -> None:
        """Navigate to the login page."""
        self.page.goto(self.base_url)
        # Wait for login screen to be visible
        self.login_screen.wait_for(state="visible")

    def enter_email(self, email: str) -> None:
        """Enter email address in the email input field."""
        self.email_input.fill(email)

    def click_continue(self) -> None:
        """Click the Continue button on the email step."""
        self.continue_button.click()

    def enter_pin(self, pin: str) -> None:
        """Enter PIN in the PIN input field."""
        self.pin_input.fill(pin)

    def enter_confirm_pin(self, pin: str) -> None:
        """Enter PIN in the confirm PIN input field."""
        self.confirm_pin_input.fill(pin)

    def click_submit(self) -> None:
        """Click the Login/Activate button on the PIN step."""
        self.submit_button.click()

    def click_back(self) -> None:
        """Click the back button to return to email step."""
        self.back_button.click()

    def get_email_error(self) -> str:
        """Get the error message displayed on the email step."""
        return self.email_message.text_content() or ""

    def get_pin_error(self) -> str:
        """Get the error message displayed on the PIN step."""
        return self.pin_message.text_content() or ""

    def get_welcome_name(self) -> str:
        """Get the welcome message displayed on the PIN step."""
        return self.welcome_name.text_content() or ""

    def get_submit_button_text(self) -> str:
        """Get the text of the submit button (Login or Activate)."""
        return self.submit_button.text_content() or ""

    def is_login_screen_visible(self) -> bool:
        """Check if the login screen is visible."""
        classes = self.login_screen.get_attribute("class") or ""
        return "hidden" not in classes

    def is_login_screen_hidden(self) -> bool:
        """Check if the login screen is hidden (user is logged in)."""
        classes = self.login_screen.get_attribute("class") or ""
        return "hidden" in classes

    def is_confirm_pin_visible(self) -> bool:
        """Check if the confirm PIN field is visible (activation mode)."""
        style = self.confirm_pin_group.get_attribute("style") or ""
        return "none" not in style

    def is_pin_step_visible(self) -> bool:
        """Check if the PIN step is currently active."""
        classes = self.page.locator("#stepPin").get_attribute("class") or ""
        return "active" in classes

    def is_email_step_visible(self) -> bool:
        """Check if the email step is currently active."""
        classes = self.page.locator("#stepEmail").get_attribute("class") or ""
        return "active" in classes

    def is_tab_bar_visible(self) -> bool:
        """Check if the tab bar is visible (indicates logged in state)."""
        classes = self.tab_bar.get_attribute("class") or ""
        return "hidden" not in classes

    def wait_for_pin_step(self) -> None:
        """Wait for the PIN step to become visible."""
        self.page.locator("#stepPin.active").wait_for(state="visible")

    def wait_for_email_step(self) -> None:
        """Wait for the email step to become visible."""
        self.page.locator("#stepEmail.active").wait_for(state="visible")

    def wait_for_logged_in(self) -> None:
        """Wait until the user is logged in (login screen hidden)."""
        self.login_screen.wait_for(state="hidden")

    def wait_for_pin_error(self) -> None:
        """Wait for a PIN error message to appear."""
        expect(self.pin_message).not_to_be_empty()

    def wait_for_email_error(self) -> None:
        """Wait for an email error message to appear."""
        expect(self.email_message).not_to_be_empty()

    def clear_local_storage(self) -> None:
        """Clear browser local storage to simulate a fresh session."""
        self.page.evaluate("localStorage.clear()")

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload()
