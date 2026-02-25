from datetime import date
from decimal import Decimal

import allure
import pytest

from carry_on.domain.course.aggregates.round import Round, RoundId
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.round_status import RoundStatus
from carry_on.domain.course.value_objects.stableford_score import StablefordScore


@allure.feature("Domain Model")
@allure.story("Round Aggregate")
class TestRoundCreation:
    def test_create_round(self) -> None:
        """Should create round with a course."""
        round = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round.course_name == "Old Course, St Andrews Links, Scotland"
        assert round.date == date(2024, 1, 15)
        assert round.id is None

    def test_create_round_with_id(self) -> None:
        """Should create successful stroke with provided ID."""
        round_id = RoundId(value="round123")
        round = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            id=round_id,
        )
        assert round.id == round_id

    def test_round_requires_a_course_name(self) -> None:
        """Successful stroke without distance should raise error."""
        with pytest.raises(ValueError, match="Course name required"):
            Round(
                id=None,
                course_name="",
                date=date(2024, 1, 15),
            )


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Player Handicap")
class TestRoundPlayerHandicap:
    """Tests for player handicap snapshot on Round."""

    def test_round_defaults_player_handicap_to_none(self) -> None:
        """Round created without handicap should default to None."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.player_handicap is None

    def test_create_round_with_player_handicap(self) -> None:
        """Round created with a handicap should store it."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
        )
        assert round_.player_handicap == Decimal("18.4")

    def test_create_round_with_explicit_none_handicap(self) -> None:
        """Explicit None handicap should be accepted."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            player_handicap=None,
        )
        assert round_.player_handicap is None


@allure.feature("Domain Model")
@allure.story("Round Entity")
class TestRoundAttributes:
    def test_round_has_all_required_attributes(self) -> None:
        """Round should expose all required attributes."""
        stroke = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert hasattr(stroke, "id")
        assert hasattr(stroke, "course_name")
        assert hasattr(stroke, "date")


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Holes")
class TestRoundHoles:
    def test_new_round_starts_with_empty_holes(self) -> None:
        """A newly created round should have no hole results."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.holes == []

    def test_record_hole_adds_hole_result(self) -> None:
        """Recording a hole should add it to the round's holes."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        round_.record_hole(hole)
        assert len(round_.holes) == 1
        assert round_.holes[0] == hole

    def test_record_hole_rejects_duplicate_hole_number(self) -> None:
        """Recording the same hole number twice should raise an error."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        round_.record_hole(hole)
        duplicate = HoleResult(hole_number=1, strokes=5, par=4, stroke_index=7)
        with pytest.raises(ValueError, match="Hole 1 already recorded"):
            round_.record_hole(duplicate)

    def test_total_strokes_returns_sum(self) -> None:
        """Total strokes should be the sum of all recorded hole strokes."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7))
        round_.record_hole(HoleResult(hole_number=2, strokes=3, par=3, stroke_index=15))
        round_.record_hole(HoleResult(hole_number=3, strokes=5, par=5, stroke_index=3))
        assert round_.total_strokes == 12

    def test_total_strokes_returns_zero_when_no_holes(self) -> None:
        """Total strokes should be 0 for a round with no recorded holes."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.total_strokes == 0

    def test_is_complete_returns_false_when_fewer_than_18_holes(self) -> None:
        """A round with fewer than 18 holes is not complete."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7))
        assert round_.is_complete is False

    def test_is_complete_returns_true_when_all_18_holes_recorded(self) -> None:
        """A round with all 18 holes recorded is complete."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        assert round_.is_complete is True

    def test_direct_constructor_starts_with_empty_holes(self) -> None:
        """Round created via direct constructor should also have empty holes."""
        round_ = Round(
            id=None,
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.holes == []

    def test_update_hole_replaces_existing_hole_result(self) -> None:
        """Updating a hole should replace the existing result."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        original = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)
        round_.record_hole(original)

        updated = HoleResult(hole_number=1, strokes=5, par=4, stroke_index=7)
        round_.update_hole(updated)

        assert len(round_.holes) == 1
        assert round_.holes[0].strokes == 5

    def test_update_hole_raises_error_if_hole_not_recorded(self) -> None:
        """Updating a non-existent hole should raise an error."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7)

        with pytest.raises(ValueError, match="Hole 1 not yet recorded"):
            round_.update_hole(hole)

    def test_round_allows_partial_holes(self) -> None:
        """Round can exist with fewer than 18 holes."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        round_.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7))
        round_.record_hole(HoleResult(hole_number=2, strokes=3, par=3, stroke_index=15))

        assert len(round_.holes) == 2
        assert round_.is_complete is False


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Status")
class TestRoundStatus:
    """Tests for round status field and transitions."""

    def test_new_round_defaults_to_in_progress(self) -> None:
        """A newly created round should default to IN_PROGRESS status."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round_.status == RoundStatus.IN_PROGRESS

    def test_create_round_with_specific_status(self) -> None:
        """Should be able to create a round with a specific status."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            status=RoundStatus.FINISHED,
        )
        assert round_.status == RoundStatus.FINISHED

    def test_finish_transitions_in_progress_to_finished(self) -> None:
        """Calling finish() should transition IN_PROGRESS to FINISHED."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        # Add 9 holes to meet the finish requirement
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.status == RoundStatus.FINISHED

    def test_finish_raises_error_if_already_finished(self) -> None:
        """Calling finish() on an already finished round should raise an error."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            status=RoundStatus.FINISHED,
        )
        with pytest.raises(ValueError, match="Round is already finished"):
            round_.finish()

    def test_abort_transitions_from_any_state(self) -> None:
        """Calling abort() should transition to ABORTED from any state."""
        # From IN_PROGRESS
        round1 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        round1.abort()
        assert round1.status == RoundStatus.ABORTED

        # From FINISHED
        round2 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            status=RoundStatus.FINISHED,
        )
        round2.abort()
        assert round2.status == RoundStatus.ABORTED

    def test_resume_transitions_aborted_to_in_progress(self) -> None:
        """Calling resume() should transition ABORTED to IN_PROGRESS."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            status=RoundStatus.ABORTED,
        )
        round_.resume()
        assert round_.status == RoundStatus.IN_PROGRESS

    def test_resume_raises_error_if_not_aborted(self) -> None:
        """Calling resume() on a non-aborted round should raise an error."""
        # From IN_PROGRESS
        round1 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        with pytest.raises(ValueError, match="Can only resume aborted rounds"):
            round1.resume()

        # From FINISHED
        round2 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            status=RoundStatus.FINISHED,
        )
        with pytest.raises(ValueError, match="Can only resume aborted rounds"):
            round2.resume()

    def test_status_independent_of_is_complete(self) -> None:
        """Status should be independent of is_complete property."""
        # Finished round with < 18 holes
        round1 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
            status=RoundStatus.FINISHED,
        )
        round1.record_hole(HoleResult(hole_number=1, strokes=4, par=4, stroke_index=7))
        assert round1.status == RoundStatus.FINISHED
        assert round1.is_complete is False

        # Aborted round with all 18 holes
        round2 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 19):
            round2.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round2.abort()
        assert round2.status == RoundStatus.ABORTED
        assert round2.is_complete is True

    def test_finish_requires_9_or_18_holes(self) -> None:
        """Finishing a round requires exactly 9 or 18 holes."""
        # Test with 0 holes
        round0 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        with pytest.raises(
            ValueError, match="Round must have either 9 or 18 holes to finish"
        ):
            round0.finish()

        # Test with invalid count (5 holes)
        round5 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 6):
            round5.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        with pytest.raises(
            ValueError, match="Round must have either 9 or 18 holes to finish"
        ):
            round5.finish()

        # Test with invalid count (10 holes - between 9 and 18)
        round10 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 11):
            round10.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        with pytest.raises(
            ValueError, match="Round must have either 9 or 18 holes to finish"
        ):
            round10.finish()

    def test_finish_succeeds_with_9_holes(self) -> None:
        """Finishing a round with exactly 9 holes should succeed."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.status == RoundStatus.FINISHED
        assert len(round_.holes) == 9

    def test_finish_succeeds_with_18_holes(self) -> None:
        """Finishing a round with exactly 18 holes should succeed."""
        round_ = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.status == RoundStatus.FINISHED
        assert len(round_.holes) == 18

    def test_in_progress_round_allows_any_number_of_holes(self) -> None:
        """In-progress rounds can have any number of holes."""
        # 0 holes is fine
        round0 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        assert round0.status == RoundStatus.IN_PROGRESS
        assert len(round0.holes) == 0

        # 5 holes is fine
        round5 = Round.create(
            course_name="Old Course, St Andrews Links, Scotland",
            date=date(2024, 1, 15),
        )
        for i in range(1, 6):
            round5.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        assert round5.status == RoundStatus.IN_PROGRESS
        assert len(round5.holes) == 5


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Stableford Scoring")
class TestRoundStablefordScore:
    """Tests for Stableford score calculation on round finalization."""

    def test_round_defaults_stableford_score_to_none(self) -> None:
        """A new round should not have a Stableford score yet."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
        )
        assert round_.stableford_score is None

    def test_finish_calculates_stableford_with_handicap(self) -> None:
        """Finishing a round with a handicap should calculate the score."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18"),
        )
        # 9 holes, all par 4 with 4 strokes (gross par)
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        # HI 18 halved for 9 holes → 9, 1 stroke per hole
        # Net: 4 - 1 = 3 on par 4 → net birdie → 3 pts × 9 = 27
        assert round_.stableford_score == StablefordScore(points=27)

    def test_finish_uses_default_54_when_no_handicap(self) -> None:
        """No handicap stored → default to 54 (WHS maximum)."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=None,
        )
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        # HI 54 halved for 9 holes → 27, 3 strokes per hole (27//9=3)
        # Net: 4 - 3 = 1 on par 4 → max(0, 2-(1-4)) = 5 pts × 9 = 45
        assert round_.stableford_score == StablefordScore(points=45)

    def test_finish_18_holes_calculates_stableford(self) -> None:
        """Full 18-hole round should calculate Stableford correctly."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("0"),
        )
        # All par 4, all 4 strokes → scratch par → 2 pts each
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.stableford_score == StablefordScore(points=36)

    def test_stableford_score_not_set_before_finish(self) -> None:
        """Score should remain None until finish() is called."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18"),
        )
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        # Not yet finished
        assert round_.stableford_score is None


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Slope & Course Rating")
class TestRoundSlopeAndCourseRating:
    """Tests for slope/course rating snapshots on Round."""

    def test_round_defaults_ratings_to_none(self) -> None:
        """Ratings default to None when not provided."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
        )
        assert round_.slope_rating is None
        assert round_.course_rating is None

    def test_create_round_with_ratings(self) -> None:
        """Round created with ratings should store them."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
        )
        assert round_.slope_rating == Decimal("125")
        assert round_.course_rating == Decimal("72.3")

    def test_create_round_with_only_slope_rating(self) -> None:
        """Providing only slope_rating is valid."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            slope_rating=Decimal("113"),
        )
        assert round_.slope_rating == Decimal("113")
        assert round_.course_rating is None


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Finish with Course Handicap")
class TestRoundFinishWithRatings:
    """finish() should use Course Handicap when ratings are available."""

    def test_finish_with_ratings_uses_course_handicap(self) -> None:
        """Slope 125, CR 72.3, Par 72: HI 18.4 → CH 21."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
        )
        # 18 par-4 holes, all 4 strokes (gross par)
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        # CH 21: base=1, remainder=3 → SI 1-3 get 2, SI 4-18 get 1
        # SI 1-3: net 4-2=2, eagle → 4 pts × 3 = 12
        # SI 4-18: net 4-1=3, birdie → 3 pts × 15 = 45
        # Total = 57
        assert round_.stableford_score == StablefordScore(points=57)
        assert round_.course_handicap == 21

    def test_finish_without_ratings_uses_handicap_directly(self) -> None:
        """No ratings → fall back to handicap index (same as before)."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        # HI 18.4 rounds to 18: 1 stroke per hole
        # Net 4-1=3, birdie → 3 pts × 18 = 54
        assert round_.stableford_score == StablefordScore(points=54)

    def test_finish_with_partial_ratings_falls_back(self) -> None:
        """Only slope, no course rating → fallback to direct handicap."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            slope_rating=Decimal("125"),
            course_rating=None,
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        # Partial ratings → fallback → same as no ratings: 54 points
        assert round_.stableford_score == StablefordScore(points=54)


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Course Handicap")
class TestRoundCourseHandicap:
    """Tests for persisting the computed Course Handicap on the Round."""

    def test_round_defaults_course_handicap_to_none(self) -> None:
        """A new round without num_holes should not have a course handicap."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
        )
        assert round_.course_handicap is None

    def test_create_sets_course_handicap_with_ratings(self) -> None:
        """Create with ratings + num_holes + course_par → WHS CH at creation.

        Slope 125, CR 72.3, Par 72, HI 18.4, 18 holes → CH 21.
        """
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
            num_holes=18,
            course_par=72,
        )
        assert round_.course_handicap == 21

    def test_create_sets_course_handicap_fallback(self) -> None:
        """Create without ratings → fallback halve+round. HI 18.4 → CH 18."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            num_holes=18,
        )
        assert round_.course_handicap == 18

    def test_create_defaults_to_54_when_no_player_handicap(self) -> None:
        """No player handicap → default to WHS max 54. 18-hole → CH 54."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            num_holes=18,
        )
        assert round_.course_handicap == 54

    def test_create_defaults_to_54_halved_for_9_holes(self) -> None:
        """No player handicap, 9-hole → 54/2 = 27."""
        round_ = Round.create(
            course_name="Old Course (front 9)",
            date=date(2024, 1, 15),
            num_holes=9,
        )
        assert round_.course_handicap == 27

    def test_create_sets_course_handicap_9_hole_fallback(self) -> None:
        """9-hole fallback at creation: HI 18.4 halved → 9.2 → rounds to 9."""
        round_ = Round.create(
            course_name="Old Course (front 9)",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            num_holes=9,
        )
        assert round_.course_handicap == 9

    def test_create_preserves_explicit_course_handicap(self) -> None:
        """When CH is explicitly provided, create() should NOT recompute."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
            num_holes=18,
            course_par=72,
            course_handicap=99,
        )
        assert round_.course_handicap == 99

    def test_create_with_num_holes_and_course_par(self) -> None:
        """num_holes and course_par should be stored on the Round."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            num_holes=18,
            course_par=72,
        )
        assert round_.num_holes == 18
        assert round_.course_par == 72

    def test_finish_with_ratings_sets_course_handicap(self) -> None:
        """Slope 125, CR 72.3, Par 72, HI 18.4 → CH 21 via finish()."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            slope_rating=Decimal("125"),
            course_rating=Decimal("72.3"),
            num_holes=18,
            course_par=72,
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.course_handicap == 21

    def test_finish_without_ratings_sets_course_handicap_fallback(self) -> None:
        """No ratings → round HI directly. HI 18.4 → CH 18."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            num_holes=18,
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.course_handicap == 18

    def test_finish_9_holes_with_ratings_halves_handicap_index(self) -> None:
        """9-hole with ratings halves HI first. CH 9."""
        round_ = Round.create(
            course_name="Hilly Links (front 9)",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            slope_rating=Decimal("125"),
            course_rating=Decimal("35.3"),
            num_holes=9,
            course_par=36,
        )
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        # CH = round((18.4/2) × (125/113) + (35.3 - 36))
        #    = round(9.2 × 1.10619… + (-0.7))
        #    = round(10.177… - 0.7) = round(9.477…) = 9
        assert round_.course_handicap == 9

    def test_finish_9_holes_without_ratings_halves_and_rounds(self) -> None:
        """9-hole fallback: HI 18.4 halved → 9.2 → rounds to 9."""
        round_ = Round.create(
            course_name="Old Course (front 9)",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
            num_holes=9,
        )
        for i in range(1, 10):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.course_handicap == 9

    def test_finish_backward_compat_fills_num_holes_from_holes(self) -> None:
        """Old rounds without num_holes should still finish correctly."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18.4"),
        )
        # No num_holes or course_par set
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        round_.finish()
        assert round_.num_holes == 18
        assert round_.course_par == 72
        assert round_.course_handicap == 18


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Per-Hole Stableford Points")
class TestRoundPerHoleStableford:
    """Tests for auto-computing stableford_points on each HoleResult."""

    def test_record_hole_computes_stableford_points(self) -> None:
        """record_hole auto-fills stableford_points when CH and num_holes are set."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18"),
            num_holes=18,
        )
        # CH=18 → 1 stroke per hole. Gross 5 on par 4: net 4 → 2 pts
        hole = HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1)
        round_.record_hole(hole)
        assert round_.holes[0].stableford_points == 2

    def test_record_hole_no_stableford_without_course_handicap(self) -> None:
        """stableford_points stays None when course_handicap is unavailable."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            # No num_holes → no course_handicap computed
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1)
        round_.record_hole(hole)
        assert round_.holes[0].stableford_points is None

    def test_update_hole_recomputes_stableford_points(self) -> None:
        """update_hole recalculates stableford_points when strokes change."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18"),
            num_holes=18,
        )
        # Record hole: gross 5, par 4, SI 1 → net 4 → 2 pts
        round_.record_hole(HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1))
        assert round_.holes[0].stableford_points == 2

        # Update to gross 7 → net 6 → 0 pts
        round_.update_hole(HoleResult(hole_number=1, strokes=7, par=4, stroke_index=1))
        assert round_.holes[0].stableford_points == 0

    def test_finish_backfills_per_hole_stableford_points(self) -> None:
        """finish() fills stableford_points on old rounds that lack them."""
        # Simulate an old round without num_holes (so record_hole won't compute)
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18"),
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        # Before finish, no per-hole points
        assert all(h.stableford_points is None for h in round_.holes)

        round_.finish()

        # After finish, all holes should have stableford_points
        # CH=18 → 1 stroke per hole. Gross 4 on par 4: net 3 → 3 pts
        assert all(h.stableford_points == 3 for h in round_.holes)


@allure.feature("Domain Model")
@allure.story("Round Aggregate - Per-Hole Handicap Strokes")
class TestRoundPerHoleHandicapStrokes:
    """Tests for auto-computing handicap_strokes on each HoleResult."""

    def test_record_hole_computes_handicap_strokes(self) -> None:
        """record_hole auto-fills handicap_strokes when CH and num_holes are set."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("20"),
            num_holes=18,
        )
        # CH=20 → base=1, remainder=2 → SI 1-2 get 2, SI 3+ get 1
        hole = HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1)
        round_.record_hole(hole)
        assert round_.holes[0].handicap_strokes == 2

        hole2 = HoleResult(hole_number=3, strokes=5, par=4, stroke_index=3)
        round_.record_hole(hole2)
        assert round_.holes[1].handicap_strokes == 1

    def test_record_hole_no_handicap_strokes_without_course_handicap(self) -> None:
        """handicap_strokes stays None when course_handicap is unavailable."""
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            # No num_holes → no course_handicap computed
        )
        hole = HoleResult(hole_number=1, strokes=4, par=4, stroke_index=1)
        round_.record_hole(hole)
        assert round_.holes[0].handicap_strokes is None

    def test_update_hole_recomputes_handicap_strokes(self) -> None:
        """update_hole preserves handicap_strokes after update."""
        round_ = Round.create(
            course_name="Hilly Links",
            date=date(2024, 1, 15),
            player_handicap=Decimal("20"),
            num_holes=18,
        )
        # Record hole: SI 1, CH 20 → hs=2
        round_.record_hole(HoleResult(hole_number=1, strokes=5, par=4, stroke_index=1))
        assert round_.holes[0].handicap_strokes == 2

        # Update strokes (hs stays 2 since SI unchanged)
        round_.update_hole(HoleResult(hole_number=1, strokes=7, par=4, stroke_index=1))
        assert round_.holes[0].handicap_strokes == 2

    def test_finish_backfills_per_hole_handicap_strokes(self) -> None:
        """finish() fills handicap_strokes on old rounds that lack them."""
        # Simulate an old round without num_holes (so record_hole won't compute)
        round_ = Round.create(
            course_name="Old Course",
            date=date(2024, 1, 15),
            player_handicap=Decimal("18"),
        )
        for i in range(1, 19):
            round_.record_hole(
                HoleResult(hole_number=i, strokes=4, par=4, stroke_index=i)
            )
        # Before finish, no per-hole handicap_strokes
        assert all(h.handicap_strokes is None for h in round_.holes)

        round_.finish()

        # After finish, all holes should have handicap_strokes
        # CH=18 → 1 stroke per hole (18//18=1, remainder=0)
        assert all(h.handicap_strokes == 1 for h in round_.holes)
