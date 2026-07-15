"""Integration test: scent mechanics wired into a full local match (Chapter 4).

Not a belief-map or lie-detection test (that is Chapter 6's territory) --
this only proves that after a real match, the raw scent trail data actually
reflects where an agent spent its time, which is the precondition any future
lie-detection logic (docs/tasks.md Sec. 4.3.4) will depend on.
"""

from police_thief.domain.board import BoardConfig, Position
from police_thief.domain.scent import ScentConfig
from police_thief.domain.scoring import ScoringTable
from police_thief.domain.simulation import run_local_match
from police_thief.shared.game_config import MatchParameters


def test_thief_scent_trail_concentrates_near_its_actual_path_not_elsewhere():
    """A thief fleeing toward the south-east corner leaves a hot trail there
    and a cold trail in the unvisited north-west -- exactly the asymmetry a
    future lie-detector (Chapter 6) would need to catch a false "I moved
    north" claim (docs/tasks.md Sec. 4.3.4's worked example).
    """
    params = MatchParameters(
        board=BoardConfig(grid_size=7, max_barriers=14),
        scoring=ScoringTable(),
        scent=ScentConfig(),
        cop_start=Position(0, 0),
        thief_start=Position(3, 3),
        max_moves=10,
        survival_threshold=10,
    )
    result = run_local_match(params)

    south_east_intensity = result.thief_scent.intensity_at(Position(6, 6))
    north_west_intensity = result.thief_scent.intensity_at(Position(0, 0))
    assert south_east_intensity > north_west_intensity
    assert north_west_intensity == 0.0


def test_both_sides_scent_fields_are_independent_after_a_full_match():
    params = MatchParameters(
        board=BoardConfig(grid_size=7, max_barriers=14),
        scoring=ScoringTable(),
        scent=ScentConfig(),
        cop_start=Position(0, 0),
        thief_start=Position(3, 3),
        max_moves=10,
        survival_threshold=10,
    )
    result = run_local_match(params)

    # The cop's own trail is hottest near its start/pursuit path (top-left
    # region); the thief's is hottest near its flight path (bottom-right).
    assert result.cop_scent.intensity_at(Position(0, 0)) > 0.0
    assert result.thief_scent.intensity_at(Position(0, 0)) == 0.0
