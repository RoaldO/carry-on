from playwright.sync_api import Page


class StrokePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        self.club = page.locator("#club")
        self.distance_input = page.locator("#distance")
        self.fail_checkbox = page.locator("#fail")
        self.submit_button = page.locator("#strokeForm button[type='submit']")
        self.message = page.locator("#message")
        self.recent_strokes = page.locator("#recentStrokes")

    def record_stroke(self, distance: int = 100) -> None:
        """Record a stroke with a specific distance."""
        self.club.select_option("5h")
        self.distance_input.fill(str(distance))
        self.submit_button.click()

    def record_failed_stroke(self) -> None:
        """Record a failed stroke."""
        self.club.select_option("5h")
        self.fail_checkbox.check()
        self.submit_button.click()

    def submit_without_distance_or_fail(self) -> None:
        """Submit form without distance or fail checked."""
        self.club.select_option("5h")
        self.distance_input.fill("")
        self.submit_button.click()

    def get_message(self) -> str:
        """Wait for and return the message text."""
        self.page.wait_for_function(
            """() => {
                const message = document.getElementById('message');
                return message && message.classList.contains('message');
            }"""
        )
        return self.message.text_content() or ""

    def get_recent_strokes_text(self) -> str:
        """Get the text content of the recent strokes section."""
        return self.recent_strokes.text_content() or ""

    def wait_for_recent_strokes(self) -> None:
        """Wait for recent strokes to load."""
        self.page.wait_for_function(
            """() => {
                const container = document.getElementById('recentStrokes');
                return container && !container.textContent.includes('Loading');
            }"""
        )

    def has_stroke_items(self) -> bool:
        """Check if there are stroke items displayed."""
        return self.page.locator(".stroke-item").count() > 0
