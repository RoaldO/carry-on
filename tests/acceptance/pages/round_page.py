"""Page Object Model for round registration functionality."""

from playwright.sync_api import Page, expect


class RoundPage:
    """Page object for the round registration form."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Round form elements
        self.round_date = page.locator("#roundDate")
        self.course_search = page.locator("#courseSearch")
        self.course_suggestions = page.locator("#courseSuggestions")
        self.current_hole_number = page.locator("#currentHoleNumber")
        self.current_hole_par = page.locator("#currentHolePar")
        self.hole_strokes = page.locator("#holeStrokes")
        self.prev_hole_btn = page.locator("#prevHoleBtn")
        self.next_hole_btn = page.locator("#nextHoleBtn")
        self.submit_round_btn = page.locator("#submitRoundBtn")
        self.round_message = page.locator("#roundMessage")

        # Navigation
        self.rounds_tab = page.locator(".tab[data-tab='rounds']")
        self.rounds_content = page.locator("#roundsContent")

    def goto_rounds_tab(self) -> None:
        """Navigate to the Rounds tab and wait for courses to load."""
        with self.page.expect_response("**/api/courses"):
            self.rounds_tab.click()
        self.rounds_content.wait_for(state="visible")

    def get_date_value(self) -> str:
        """Get the current value of the date input."""
        return self.round_date.input_value()

    def type_course_search(self, text: str) -> None:
        """Type text into the course search field."""
        self.course_search.fill(text)
        # Wait for suggestions to appear
        self.page.wait_for_timeout(300)

    def get_suggestions(self) -> list[str]:
        """Get the text of visible course suggestions."""
        items = self.course_suggestions.locator(".course-suggestion")
        return [items.nth(i).text_content() or "" for i in range(items.count())]

    def select_course_suggestion(self, name: str) -> None:
        """Click a course suggestion by name."""
        self.course_suggestions.locator(f"text={name}").click()
        # Wait for hole navigator to appear
        self.page.wait_for_timeout(300)

    def get_current_hole(self) -> str:
        """Get the current hole number displayed."""
        return self.current_hole_number.text_content() or ""

    def get_current_par(self) -> str:
        """Get the par displayed for the current hole."""
        return self.current_hole_par.text_content() or ""

    def enter_strokes(self, strokes: str) -> None:
        """Enter strokes for the current hole."""
        self.hole_strokes.fill(strokes)

    def click_next_hole(self) -> None:
        """Click the next hole button."""
        self.next_hole_btn.click()
        self.page.wait_for_timeout(100)

    def click_prev_hole(self) -> None:
        """Click the previous hole button."""
        self.prev_hole_btn.click()
        self.page.wait_for_timeout(100)

    def submit_round(self) -> None:
        """Click the submit round button."""
        self.submit_round_btn.click()

    def fill_all_holes(self, count: int, strokes: int = 4) -> None:
        """Fill strokes for all holes by navigating through them.

        Args:
            count: Number of holes to fill.
            strokes: Number of strokes per hole.
        """
        for i in range(count):
            self.enter_strokes(str(strokes))
            if i < count - 1:
                self.click_next_hole()

    def get_message(self) -> str:
        """Get the round message text."""
        return self.round_message.text_content() or ""

    def wait_for_message(self) -> None:
        """Wait for a round message to appear."""
        expect(self.round_message).not_to_be_empty()

    def is_hole_navigator_visible(self) -> bool:
        """Check if the hole navigator is visible."""
        return self.current_hole_number.is_visible()
