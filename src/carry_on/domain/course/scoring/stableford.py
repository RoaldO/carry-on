"""Stableford scoring calculation.

Pure functions for computing Stableford points based on gross strokes,
hole par/stroke index, and player handicap. Stateless and side-effect-free.
"""

from decimal import ROUND_HALF_UP, Decimal

from carry_on.domain.course.value_objects.hole_result import HoleResult
from carry_on.domain.course.value_objects.stableford_score import StablefordScore


def handicap_strokes_for_hole(
    handicap: int,
    stroke_index: int,
    num_holes: int,
) -> int:
    """Calculate the number of handicap strokes a player receives on a hole.

    Strokes are distributed evenly, with extra strokes going to holes
    with the lowest stroke index (hardest holes first).

    Args:
        handicap: The player's playing handicap (integer).
        stroke_index: The hole's stroke index (1 = hardest).
        num_holes: Number of holes on the course (9 or 18).

    Returns:
        Number of handicap strokes for this hole.
    """
    base = handicap // num_holes
    remainder = handicap % num_holes
    return base + (1 if stroke_index <= remainder else 0)


def stableford_points(gross_strokes: int, par: int, handicap_strokes: int) -> int:
    """Calculate Stableford points for a single hole.

    Points are based on the net score (gross strokes minus handicap strokes)
    relative to par:
        Net double bogey or worse → 0
        Net bogey → 1
        Net par → 2
        Net birdie → 3
        Net eagle → 4
        Net albatross → 5

    Args:
        gross_strokes: Gross strokes taken on the hole.
        par: The hole's par.
        handicap_strokes: Handicap strokes the player receives on this hole.

    Returns:
        Stableford points (0 or more).
    """
    net = gross_strokes - handicap_strokes
    return max(0, 2 - (net - par))


def compute_hole_stableford(
    hole: HoleResult,
    course_handicap: int,
    num_holes: int,
) -> int:
    """Compute Stableford points for a single hole.

    Convenience function that combines handicap stroke distribution
    and point calculation in one call.

    Args:
        hole: The hole result with gross strokes, par, and stroke index.
        course_handicap: The player's course handicap (integer).
        num_holes: Number of holes on the course (9 or 18).

    Returns:
        Stableford points for this hole (0 or more).
    """
    hs = handicap_strokes_for_hole(
        handicap=course_handicap,
        stroke_index=hole.stroke_index,
        num_holes=num_holes,
    )
    return stableford_points(
        gross_strokes=hole.strokes,
        par=hole.par,
        handicap_strokes=hs,
    )


def calculate_course_handicap(
    handicap_index: Decimal,
    slope_rating: Decimal,
    course_rating: Decimal,
    par: int,
    num_holes: int = 18,
) -> int:
    """Calculate Course Handicap using the WHS formula.

    18-hole: Course Handicap = round(HI × (Slope / 113) + (CR - Par))
     9-hole: Course Handicap = round((HI / 2) × (Slope / 113) + (CR - Par))

    Args:
        handicap_index: The player's handicap index.
        slope_rating: The course's slope rating (55-155).
        course_rating: The course's rating for scratch golfer.
        par: Total par of the course.
        num_holes: Number of holes on the course (9 or 18).

    Returns:
        The integer Course Handicap (rounded half-up).
    """
    effective_hi = handicap_index / 2 if num_holes == 9 else handicap_index
    neutral_slope = Decimal("113")
    raw = effective_hi * (slope_rating / neutral_slope) + (course_rating - Decimal(par))
    return int(raw.to_integral_value(rounding=ROUND_HALF_UP))


def calculate_stableford(
    holes: list[HoleResult],
    player_handicap: Decimal,
    num_holes: int,
    slope_rating: Decimal | None = None,
    course_rating: Decimal | None = None,
) -> StablefordScore:
    """Calculate the total Stableford score for a round.

    When slope_rating and course_rating are both provided, the WHS
    Course Handicap formula is used. Otherwise falls back to rounding
    the handicap index directly (equivalent to Slope=113, CR=Par).

    Args:
        holes: List of hole results with strokes, par, and stroke_index.
        player_handicap: The player's handicap index (Decimal).
        num_holes: Number of holes on the course (9 or 18).
        slope_rating: Optional course slope rating.
        course_rating: Optional course rating.

    Returns:
        A StablefordScore value object with the total points.
    """
    if slope_rating is not None and course_rating is not None:
        par = sum(h.par for h in holes)
        playing_handicap = calculate_course_handicap(
            handicap_index=player_handicap,
            slope_rating=slope_rating,
            course_rating=course_rating,
            par=par,
            num_holes=num_holes,
        )
    else:
        effective_handicap = player_handicap / 2 if num_holes == 9 else player_handicap
        playing_handicap = int(
            effective_handicap.to_integral_value(rounding=ROUND_HALF_UP)
        )

    total = 0
    for hole in holes:
        strokes_for_hole = handicap_strokes_for_hole(
            handicap=playing_handicap,
            stroke_index=hole.stroke_index,
            num_holes=num_holes,
        )
        total += stableford_points(
            gross_strokes=hole.strokes,
            par=hole.par,
            handicap_strokes=strokes_for_hole,
        )

    return StablefordScore(points=total)
