from decimal import Decimal

import allure
import pytest

from carry_on.domain.course.aggregates.course import Course, CourseId
from carry_on.domain.course.value_objects.hole import Hole


def _make_holes(n: int) -> tuple[Hole, ...]:
    """Helper to create a valid sequence of n holes."""
    pars = [4, 4, 3, 5, 4, 3, 4, 5, 4, 4, 4, 3, 5, 4, 3, 4, 5, 4]
    return tuple(
        Hole(hole_number=i + 1, par=pars[i % len(pars)], stroke_index=i + 1)
        for i in range(n)
    )


@allure.feature("Domain Model")
@allure.story("Course Aggregate")
class TestCourseCreation:
    def test_create_valid_18_hole_course(self) -> None:
        """Should create an 18-hole course via factory method."""
        holes = _make_holes(18)
        course = Course.create(name="Old Course, St Andrews", holes=holes)
        assert course.name == "Old Course, St Andrews"
        assert len(course.holes) == 18
        assert course.id is None

    def test_create_valid_9_hole_course(self) -> None:
        """Should create a 9-hole course via factory method."""
        holes = _make_holes(9)
        course = Course.create(name="Short Course", holes=holes)
        assert course.name == "Short Course"
        assert len(course.holes) == 9

    def test_create_course_with_id(self) -> None:
        """Should create a course with a provided ID."""
        course_id = CourseId(value="course-123")
        holes = _make_holes(18)
        course = Course.create(name="Old Course, St Andrews", holes=holes, id=course_id)
        assert course.id == course_id


@allure.feature("Domain Model")
@allure.story("Course Aggregate - Validation")
class TestCourseValidation:
    def test_rejects_empty_name(self) -> None:
        """Course name is required."""
        holes = _make_holes(18)
        with pytest.raises(ValueError, match="Course name required"):
            Course.create(name="", holes=holes)

    def test_rejects_whitespace_only_name(self) -> None:
        """Whitespace-only name is rejected."""
        holes = _make_holes(18)
        with pytest.raises(ValueError, match="Course name required"):
            Course.create(name="   ", holes=holes)

    def test_rejects_wrong_number_of_holes_seven(self) -> None:
        """A course must have exactly 9 or 18 holes, not 7."""
        holes = _make_holes(7)
        with pytest.raises(ValueError, match="Course must have exactly 9 or 18 holes"):
            Course.create(name="Bad Course", holes=holes)

    def test_rejects_wrong_number_of_holes_twelve(self) -> None:
        """A course must have exactly 9 or 18 holes, not 12."""
        holes = _make_holes(12)
        with pytest.raises(ValueError, match="Course must have exactly 9 or 18 holes"):
            Course.create(name="Bad Course", holes=holes)

    def test_rejects_duplicate_hole_numbers(self) -> None:
        """Hole numbers must be unique."""
        holes = tuple(Hole(hole_number=1, par=4, stroke_index=i + 1) for i in range(9))
        with pytest.raises(ValueError, match="Hole numbers must be sequential"):
            Course.create(name="Bad Course", holes=holes)

    def test_rejects_non_sequential_hole_numbers(self) -> None:
        """Hole numbers must be 1 through N in sequence."""
        holes = tuple(Hole(hole_number=i, par=4, stroke_index=i) for i in range(2, 11))
        with pytest.raises(ValueError, match="Hole numbers must be sequential"):
            Course.create(name="Bad Course", holes=holes)

    def test_rejects_duplicate_stroke_indices(self) -> None:
        """Stroke indices must be unique."""
        holes = tuple(Hole(hole_number=i + 1, par=4, stroke_index=1) for i in range(9))
        with pytest.raises(
            ValueError, match="Stroke indices must be unique and cover 1"
        ):
            Course.create(name="Bad Course", holes=holes)

    def test_rejects_stroke_indices_not_covering_1_to_n(self) -> None:
        """Stroke indices must cover exactly 1 through N."""
        holes = tuple(
            Hole(hole_number=i + 1, par=4, stroke_index=i + 2) for i in range(9)
        )
        with pytest.raises(
            ValueError, match="Stroke indices must be unique and cover 1"
        ):
            Course.create(name="Bad Course", holes=holes)


@allure.feature("Domain Model")
@allure.story("Course Aggregate - Properties")
class TestCourseProperties:
    def test_total_par(self) -> None:
        """Total par should be the sum of all hole pars."""
        holes = _make_holes(18)
        course = Course.create(name="Old Course", holes=holes)
        expected_par = sum(h.par for h in holes)
        assert course.total_par == expected_par

    def test_total_par_nine_holes(self) -> None:
        """Total par for a 9-hole course."""
        holes = _make_holes(9)
        course = Course.create(name="Short Course", holes=holes)
        expected_par = sum(h.par for h in holes)
        assert course.total_par == expected_par

    def test_number_of_holes_eighteen(self) -> None:
        """Should report 18 holes."""
        holes = _make_holes(18)
        course = Course.create(name="Old Course", holes=holes)
        assert course.number_of_holes == 18

    def test_number_of_holes_nine(self) -> None:
        """Should report 9 holes."""
        holes = _make_holes(9)
        course = Course.create(name="Short Course", holes=holes)
        assert course.number_of_holes == 9


@allure.feature("Domain Model")
@allure.story("Course Aggregate - Slope & Course Rating")
class TestCourseSlopeAndCourseRating:
    def test_create_course_with_ratings(self) -> None:
        """Should store slope and course rating on creation."""
        holes = _make_holes(18)
        course = Course.create(
            name="Hilly Links",
            holes=holes,
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
        )
        assert course.slope_rating == Decimal("125")
        assert course.course_rating == Decimal("72.3")

    def test_ratings_default_to_none(self) -> None:
        """Ratings are optional and default to None."""
        holes = _make_holes(18)
        course = Course.create(name="Old Course", holes=holes)
        assert course.slope_rating is None
        assert course.course_rating is None

    def test_rejects_slope_rating_below_55(self) -> None:
        """WHS slope rating minimum is 55."""
        holes = _make_holes(18)
        with pytest.raises(ValueError, match="Slope rating must be between 55 and 155"):
            Course.create(
                name="Bad Course",
                holes=holes,
                slope_rating=Decimal("54"),
            )

    def test_rejects_slope_rating_above_155(self) -> None:
        """WHS slope rating maximum is 155."""
        holes = _make_holes(18)
        with pytest.raises(ValueError, match="Slope rating must be between 55 and 155"):
            Course.create(
                name="Bad Course",
                holes=holes,
                slope_rating=Decimal("156"),
            )

    def test_accepts_slope_rating_at_boundaries(self) -> None:
        """Slope rating 55 and 155 are both valid."""
        holes = _make_holes(18)
        course_low = Course.create(
            name="Easy Course",
            holes=holes,
            slope_rating=Decimal("55"),
        )
        course_high = Course.create(
            name="Hard Course",
            holes=holes,
            slope_rating=Decimal("155"),
        )
        assert course_low.slope_rating == Decimal("55")
        assert course_high.slope_rating == Decimal("155")

    def test_rejects_non_positive_course_rating(self) -> None:
        """Course rating must be positive."""
        holes = _make_holes(18)
        with pytest.raises(ValueError, match="Course rating must be positive"):
            Course.create(
                name="Bad Course",
                holes=holes,
                course_rating=Decimal("0"),
            )

    def test_rejects_negative_course_rating(self) -> None:
        """Negative course rating is rejected."""
        holes = _make_holes(18)
        with pytest.raises(ValueError, match="Course rating must be positive"):
            Course.create(
                name="Bad Course",
                holes=holes,
                course_rating=Decimal("-1.5"),
            )
