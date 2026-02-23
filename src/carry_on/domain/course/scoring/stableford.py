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


def stableford_points(strokes: int, par: int, handicap_strokes: int) -> int:
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
        strokes: Gross strokes taken on the hole.
        par: The hole's par.
        handicap_strokes: Handicap strokes the player receives on this hole.

    Returns:
        Stableford points (0 or more).
    """
    net = strokes - handicap_strokes
    return max(0, 2 - (net - par))


def calculate_stableford(
    holes: list[HoleResult],
    player_handicap: Decimal,
    num_holes: int,
) -> StablefordScore:
    """Calculate the total Stableford score for a round.

    Args:
        holes: List of hole results with strokes, par, and stroke_index.
        player_handicap: The player's handicap index (Decimal, rounded to int).
        num_holes: Number of holes on the course (9 or 18).

    Returns:
        A StablefordScore value object with the total points.
    """
    playing_handicap = int(player_handicap.to_integral_value(rounding=ROUND_HALF_UP))

    total = 0
    for hole in holes:
        strokes_for_hole = handicap_strokes_for_hole(
            handicap=playing_handicap,
            stroke_index=hole.stroke_index,
            num_holes=num_holes,
        )
        total += stableford_points(
            strokes=hole.strokes,
            par=hole.par,
            handicap_strokes=strokes_for_hole,
        )

    return StablefordScore(points=total)
