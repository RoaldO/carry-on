"""Page Object Model for course management functionality."""

from playwright.sync_api import Page, expect


class CoursePage:
    """Page object for the courses management page."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        # Navigation
        self.profile_tab = page.locator(".tab[data-tab='profile']")
        self.my_courses_link = page.locator("#myCoursesLink")
        self.courses_content = page.locator("#coursesContent")

        # Course list
        self.course_list = page.locator("#courseList")
        self.add_course_button = page.locator("#addCourseBtn")

        # Course form
        self.course_form = page.locator("#courseForm")
        self.course_name_input = page.locator("#courseName")
        self.holes_9_button = page.locator("#holes9Btn")
        self.holes_18_button = page.locator("#holes18Btn")
        self.hole_details_table = page.locator("#holeDetailsTable")
        self.save_course_button = page.locator("#saveCourseBtn")
        self.cancel_course_button = page.locator("#cancelCourseBtn")
        self.course_form_error = page.locator("#courseFormError")

    def navigate_to_courses(self) -> None:
        """Navigate to the courses page via profile tab."""
        self.profile_tab.click()
        # Wait for profile to load
        self.page.wait_for_function(
            "document.getElementById('profileName').textContent !== 'Loading...'"
        )
        self.my_courses_link.click()
        self.courses_content.wait_for(state="visible")

    def click_add_course(self) -> None:
        """Click the Add Course button."""
        self.add_course_button.click()
        self.course_form.wait_for(state="visible")

    def enter_course_name(self, name: str) -> None:
        """Enter the course name."""
        self.course_name_input.fill(name)

    def select_hole_count(self, count: int) -> None:
        """Select 9 or 18 holes."""
        if count == 9:
            self.holes_9_button.click()
        elif count == 18:
            self.holes_18_button.click()

    def fill_hole_details(self, count: int) -> None:
        """Fill in par and stroke index for all holes with defaults.

        Par defaults to 4, stroke index is sequential (already set by UI).
        """
        # The UI should pre-fill defaults, so we just verify the table has rows
        # and let the defaults stand (par=4, stroke_index=sequential)
        for i in range(count):
            par_select = self.page.locator(f"#par_{i + 1}")
            expect(par_select).to_be_visible()

    def submit_course_form(self) -> None:
        """Click the Save Course button."""
        self.save_course_button.click()

    def is_course_in_list(self, name: str) -> bool:
        """Check if a course appears in the course list."""
        return self.course_list.locator(f"text={name}").is_visible()

    def wait_for_course_in_list(self, name: str) -> None:
        """Wait for a course to appear in the list."""
        self.course_list.locator(f"text={name}").wait_for(state="visible")

    def has_form_error(self) -> bool:
        """Check if a form error message is visible."""
        return self.course_form_error.is_visible()

    def wait_for_form_error(self) -> None:
        """Wait for a form error to appear."""
        expect(self.course_form_error).to_be_visible()

    def reload(self) -> None:
        """Reload the page and navigate back to courses."""
        self.page.reload()
        # Wait for login to complete (auto-login via stored credentials)
        self.page.wait_for_function(
            """() => {
                const tabBar = document.getElementById('tabBar');
                return tabBar && !tabBar.classList.contains('hidden');
            }"""
        )
        self.navigate_to_courses()
