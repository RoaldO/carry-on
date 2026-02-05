from playwright.sync_api import Page


class IdeasPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        self.ideas_tab = page.locator('[data-tab="ideas"]')
        self.description_input = page.locator("#ideaDescription")
        self.submit_button = page.locator("#ideaForm button[type='submit']")
        self.message = page.locator("#ideaMessage")
        self.char_counter = page.locator("#charCount")

    def goto_ideas_tab(self) -> None:
        """Navigate to the Ideas tab."""
        self.ideas_tab.click()
        self.page.wait_for_selector("#ideasContent.active")

    def submit_idea(self, description: str) -> None:
        """Submit an idea with the given description."""
        self.description_input.fill(description)
        self.submit_button.click()

    def try_submit_empty(self) -> None:
        """Try to submit with empty description."""
        self.description_input.fill("")
        self.submit_button.click()

    def type_idea(self, text: str) -> None:
        """Type text into the idea description field."""
        self.description_input.fill(text)

    def get_message(self) -> str:
        """Wait for and return the message text."""
        self.page.wait_for_function(
            """() => {
                const message = document.getElementById('ideaMessage');
                return message && message.classList.contains('message');
            }"""
        )
        return self.message.text_content() or ""

    def get_char_count(self) -> int:
        """Get the current character count displayed."""
        text = self.char_counter.text_content() or "0"
        return int(text)

    def is_form_valid(self) -> bool:
        """Check if the form would be valid for submission."""
        return self.description_input.evaluate("el => el.validity.valid")
