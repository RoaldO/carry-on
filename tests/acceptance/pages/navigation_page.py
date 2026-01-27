"""Page Object Model for navigation and profile functionality."""

from playwright.sync_api import Page


class NavigationPage:
    """Page object for tab navigation and profile functionality."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Tab bar elements
        self.tab_bar = page.locator("#tabBar")
        self.strokes_tab = page.locator(".tab[data-tab='strokes']")
        self.ideas_tab = page.locator(".tab[data-tab='ideas']")
        self.profile_tab = page.locator(".tab[data-tab='profile']")

        # Content sections
        self.strokes_content = page.locator("#strokesContent")
        self.ideas_content = page.locator("#ideasContent")
        self.profile_content = page.locator("#profileContent")

        # Profile elements
        self.profile_name = page.locator("#profileName")
        self.profile_email = page.locator("#profileEmail")
        self.logout_button = page.locator("#logoutBtn")

        # Login screen
        self.login_screen = page.locator("#loginScreen")

    def is_tab_bar_visible(self) -> bool:
        """Check if the tab bar is visible."""
        classes = self.tab_bar.get_attribute("class") or ""
        return "hidden" not in classes

    def is_strokes_tab_visible(self) -> bool:
        """Check if Strokes tab button exists."""
        return self.strokes_tab.is_visible()

    def is_ideas_tab_visible(self) -> bool:
        """Check if Ideas tab button exists."""
        return self.ideas_tab.is_visible()

    def is_profile_tab_visible(self) -> bool:
        """Check if Profile tab button exists."""
        return self.profile_tab.is_visible()

    def click_strokes_tab(self) -> None:
        """Click the Strokes tab."""
        self.strokes_tab.click()

    def click_ideas_tab(self) -> None:
        """Click the Ideas tab."""
        self.ideas_tab.click()

    def click_profile_tab(self) -> None:
        """Click the Profile tab."""
        self.profile_tab.click()

    def is_on_strokes_tab(self) -> bool:
        """Check if Strokes tab content is visible."""
        return self.strokes_content.is_visible()

    def is_on_ideas_tab(self) -> bool:
        """Check if Ideas tab content is visible."""
        return self.ideas_content.is_visible()

    def is_on_profile_tab(self) -> bool:
        """Check if Profile tab content is visible."""
        return self.profile_content.is_visible()

    def is_strokes_tab_active(self) -> bool:
        """Check if Strokes tab is marked active."""
        classes = self.strokes_tab.get_attribute("class") or ""
        return "active" in classes

    def is_ideas_tab_active(self) -> bool:
        """Check if Ideas tab is marked active."""
        classes = self.ideas_tab.get_attribute("class") or ""
        return "active" in classes

    def is_profile_tab_active(self) -> bool:
        """Check if Profile tab is marked active."""
        classes = self.profile_tab.get_attribute("class") or ""
        return "active" in classes

    def get_current_url_hash(self) -> str:
        """Get the current URL hash."""
        return self.page.evaluate("window.location.hash")

    def navigate_to_hash(self, hash_value: str) -> None:
        """Navigate to a specific URL hash."""
        # Handle both "/#ideas" and "#ideas" formats
        url = f"{self.base_url}{hash_value}" if hash_value.startswith("/") else f"{self.base_url}/{hash_value}"
        self.page.goto(url)
        # Wait for page to load and login to complete (tab bar becomes visible)
        self.page.wait_for_function(
            """() => {
                const tabBar = document.getElementById('tabBar');
                return tabBar && !tabBar.classList.contains('hidden');
            }"""
        )
        # Wait for hash change to take effect
        self.page.wait_for_timeout(300)

    def get_profile_name(self) -> str:
        """Get the displayed profile name."""
        self.page.wait_for_timeout(500)  # Wait for API call
        return self.profile_name.text_content() or ""

    def get_profile_email(self) -> str:
        """Get the displayed profile email."""
        self.page.wait_for_timeout(500)  # Wait for API call
        return self.profile_email.text_content() or ""

    def is_logout_button_visible(self) -> bool:
        """Check if logout button is visible."""
        return self.logout_button.is_visible()

    def click_logout(self) -> None:
        """Click the logout button."""
        self.logout_button.click()

    def is_login_screen_visible(self) -> bool:
        """Check if login screen is visible."""
        classes = self.login_screen.get_attribute("class") or ""
        return "hidden" not in classes

    def wait_for_profile_loaded(self) -> None:
        """Wait for profile data to load."""
        self.page.wait_for_function(
            "document.getElementById('profileName').textContent !== 'Loading...'"
        )

    def reload(self) -> None:
        """Reload the page."""
        self.page.reload()
