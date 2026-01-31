from playwright.sync_api import Page


class StrokePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        self.club = page.locator("#club")
        self.distance_input = page.locator("#distance")
        self.submit_button = page.locator("#strokeForm button[type='submit']")
        self.message = page.locator("#message")

    def record_stroke(self):
        self.club.select_option("5h")
        self.distance_input.fill("100")
        self.submit_button.click()

    def get_message(self):
        self.page.wait_for_function(
            """() => {
                const message = document.getElementById('message');
                return message && message.classList.contains('message');
            }"""
        )
        return self.message.text_content()
