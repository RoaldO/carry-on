from decimal import Decimal

import allure

from carry_on.domain.course.scoring.stableford import (
    calculate_stableford,
    handicap_strokes_for_hole,
    stableford_points,
)
from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.stableford_score import StablefordScore


@allure.feature("Domain Model")
@allure.story("Stableford Calculation - Handicap Strokes")
class TestHandicapStrokesForHole:
    """Handicap strokes are distributed by stroke index.

    For N holes and playing handicap H:
    - base = H // N (everyone gets at least this)
    - remainder = H % N (holes with stroke_index <= remainder get +1)
    """

    def test_exact_handicap_18_on_18_holes(self) -> None:
        """Handicap 18 = exactly 1 stroke per hole on 18 holes."""
        assert handicap_strokes_for_hole(handicap=18, stroke_index=1, num_holes=18) == 1
        assert (
            handicap_strokes_for_hole(handicap=18, stroke_index=18, num_holes=18) == 1
        )

    def test_handicap_20_extra_strokes_go_to_lowest_si(self) -> None:
        """Handicap 20 on 18 holes: SI 1-2 get 2 strokes, SI 3+ get 1."""
        assert handicap_strokes_for_hole(handicap=20, stroke_index=1, num_holes=18) == 2
        assert handicap_strokes_for_hole(handicap=20, stroke_index=2, num_holes=18) == 2
        assert handicap_strokes_for_hole(handicap=20, stroke_index=3, num_holes=18) == 1
        assert (
            handicap_strokes_for_hole(handicap=20, stroke_index=18, num_holes=18) == 1
        )

    def test_nine_hole_round(self) -> None:
        """Handicap 10 on 9 holes: SI 1 gets 2 strokes, SI 2+ get 1."""
        assert handicap_strokes_for_hole(handicap=10, stroke_index=1, num_holes=9) == 2
        assert handicap_strokes_for_hole(handicap=10, stroke_index=2, num_holes=9) == 1

    def test_handicap_zero(self) -> None:
        """Scratch golfer gets no extra strokes."""
        assert handicap_strokes_for_hole(handicap=0, stroke_index=1, num_holes=18) == 0

    def test_handicap_36_on_18_holes(self) -> None:
        """Handicap 36 = exactly 2 strokes per hole."""
        assert handicap_strokes_for_hole(handicap=36, stroke_index=1, num_holes=18) == 2
        assert (
            handicap_strokes_for_hole(handicap=36, stroke_index=18, num_holes=18) == 2
        )

    def test_handicap_54_on_18_holes(self) -> None:
        """WHS maximum: handicap 54 = 3 strokes per hole on 18 holes."""
        assert handicap_strokes_for_hole(handicap=54, stroke_index=1, num_holes=18) == 3
        assert (
            handicap_strokes_for_hole(handicap=54, stroke_index=18, num_holes=18) == 3
        )


@allure.feature("Domain Model")
@allure.story("Stableford Calculation - Points Per Hole")
class TestStablefordPoints:
    """Stableford points based on net score vs par.

    Formula: max(0, 2 - (net_strokes - par))
    where net_strokes = strokes - handicap_strokes
    """

    def test_net_par_scores_two_points(self) -> None:
        """Par 4, 4 strokes, 0 handicap strokes → net par → 2 pts."""
        assert stableford_points(strokes=4, par=4, handicap_strokes=0) == 2

    def test_net_bogey_scores_one_point(self) -> None:
        """Par 4, 5 strokes, 0 handicap strokes → net bogey → 1 pt."""
        assert stableford_points(strokes=5, par=4, handicap_strokes=0) == 1

    def test_net_birdie_scores_three_points(self) -> None:
        """Par 4, 3 strokes, 0 handicap strokes → net birdie → 3 pts."""
        assert stableford_points(strokes=3, par=4, handicap_strokes=0) == 3

    def test_net_eagle_scores_four_points(self) -> None:
        """Par 4, 2 strokes, 0 handicap strokes → net eagle → 4 pts."""
        assert stableford_points(strokes=2, par=4, handicap_strokes=0) == 4

    def test_net_double_bogey_or_worse_scores_zero(self) -> None:
        """Par 4, 6+ strokes, 0 handicap → net double bogey+ → 0 pts."""
        assert stableford_points(strokes=6, par=4, handicap_strokes=0) == 0
        assert stableford_points(strokes=10, par=4, handicap_strokes=0) == 0

    def test_handicap_strokes_improve_net_score(self) -> None:
        """Par 4, 5 gross strokes, 1 handicap stroke → net par → 2 pts."""
        assert stableford_points(strokes=5, par=4, handicap_strokes=1) == 2

    def test_two_handicap_strokes(self) -> None:
        """Par 4, 6 gross strokes, 2 handicap strokes → net par → 2 pts."""
        assert stableford_points(strokes=6, par=4, handicap_strokes=2) == 2

    def test_par_3_with_handicap(self) -> None:
        """Par 3, 4 gross strokes, 1 handicap stroke → net par → 2 pts."""
        assert stableford_points(strokes=4, par=3, handicap_strokes=1) == 2

    def test_par_5_net_birdie(self) -> None:
        """Par 5, 5 gross strokes, 1 handicap stroke → net birdie → 3 pts."""
        assert stableford_points(strokes=5, par=5, handicap_strokes=1) == 3


@allure.feature("Domain Model")
@allure.story("Stableford Calculation - Total Score")
class TestCalculateStableford:
    """End-to-end calculation: holes + handicap → StablefordScore."""

    def test_all_pars_handicap_zero_18_holes(self) -> None:
        """All pars on scratch handicap = 36 points (18 × 2)."""
        holes = [
            HoleResult(hole_number=i + 1, strokes=4, par=4, stroke_index=i + 1)
            for i in range(18)
        ]
        result = calculate_stableford(
            holes=holes,
            player_handicap=Decimal("0"),
            num_holes=18,
        )
        assert result == StablefordScore(points=36)

    def test_all_pars_handicap_18_means_36_points(self) -> None:
        """Handicap 18: each hole net = 4-1 = 3 (birdie) → 3 pts × 18."""
        holes = [
            HoleResult(hole_number=i + 1, strokes=4, par=4, stroke_index=i + 1)
            for i in range(18)
        ]
        result = calculate_stableford(
            holes=holes,
            player_handicap=Decimal("18"),
            num_holes=18,
        )
        # Net score per hole: 4 - 1 = 3, which is net birdie on par 4 → 3 points
        assert result == StablefordScore(points=54)

    def test_nine_hole_round(self) -> None:
        """9-hole round with handicap 9: each hole gets 1 stroke."""
        holes = [
            HoleResult(hole_number=i + 1, strokes=5, par=4, stroke_index=i + 1)
            for i in range(9)
        ]
        result = calculate_stableford(
            holes=holes,
            player_handicap=Decimal("9"),
            num_holes=9,
        )
        # Gross bogey (5) - 1 handicap = net par (4) → 2 points × 9
        assert result == StablefordScore(points=18)

    def test_rounds_decimal_handicap(self) -> None:
        """Decimal handicap 18.4 rounds to 18 for stroke distribution."""
        holes = [
            HoleResult(hole_number=i + 1, strokes=4, par=4, stroke_index=i + 1)
            for i in range(18)
        ]
        result = calculate_stableford(
            holes=holes,
            player_handicap=Decimal("18.4"),
            num_holes=18,
        )
        # Same as handicap 18: net birdie each hole → 3 pts × 18 = 54
        assert result == StablefordScore(points=54)

    def test_mixed_scores(self) -> None:
        """Realistic round with varied strokes and handicap 10."""
        holes = [
            # SI 1-10 get 1 handicap stroke, SI 11-18 get 0
            HoleResult(
                hole_number=1, strokes=5, par=4, stroke_index=1
            ),  # net 4, par → 2
            HoleResult(
                hole_number=2, strokes=4, par=4, stroke_index=2
            ),  # net 3, birdie → 3
            HoleResult(
                hole_number=3, strokes=4, par=3, stroke_index=3
            ),  # net 3, par → 2
            HoleResult(
                hole_number=4, strokes=6, par=5, stroke_index=4
            ),  # net 5, par → 2
            HoleResult(
                hole_number=5, strokes=5, par=4, stroke_index=5
            ),  # net 4, par → 2
            HoleResult(
                hole_number=6, strokes=3, par=3, stroke_index=6
            ),  # net 2, birdie → 3
            HoleResult(
                hole_number=7, strokes=5, par=4, stroke_index=7
            ),  # net 4, par → 2
            HoleResult(
                hole_number=8, strokes=7, par=5, stroke_index=8
            ),  # net 6, bogey → 1
            HoleResult(
                hole_number=9, strokes=4, par=4, stroke_index=9
            ),  # net 3, birdie → 3
            HoleResult(
                hole_number=10, strokes=5, par=4, stroke_index=10
            ),  # net 4, par → 2
            HoleResult(
                hole_number=11, strokes=5, par=4, stroke_index=11
            ),  # net 5, bogey → 1
            HoleResult(
                hole_number=12, strokes=4, par=3, stroke_index=12
            ),  # net 4, bogey → 1
            HoleResult(
                hole_number=13, strokes=6, par=5, stroke_index=13
            ),  # net 6, bogey → 1
            HoleResult(
                hole_number=14, strokes=4, par=4, stroke_index=14
            ),  # net 4, par → 2
            HoleResult(
                hole_number=15, strokes=3, par=3, stroke_index=15
            ),  # net 3, par → 2
            HoleResult(
                hole_number=16, strokes=5, par=4, stroke_index=16
            ),  # net 5, bogey → 1
            HoleResult(
                hole_number=17, strokes=6, par=5, stroke_index=17
            ),  # net 6, bogey → 1
            HoleResult(
                hole_number=18, strokes=5, par=4, stroke_index=18
            ),  # net 5, bogey → 1
        ]
        result = calculate_stableford(
            holes=holes,
            player_handicap=Decimal("10"),
            num_holes=18,
        )
        # Sum: 2+3+2+2+2+3+2+1+3+2+1+1+1+2+2+1+1+1 = 32
        assert result == StablefordScore(points=32)
