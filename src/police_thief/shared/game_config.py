"""Loader for the shared, signed match config: config/game.json.

docs/tasks.md Sec. 3.1.2: all physical laws come from one pre-agreed file
both sides load identically -- board dimensions, starting positions, the
barrier set, and the scoring table -- as hard-coded values, never
renegotiated mid-match. Cryptographically locking this file so neither side
can silently diverge after Step-0 is Chapter 5/6's concern; this loader only
parses and validates structure/minimums for now.

Position arrays in the JSON are `[row, col]`, matching domain.board.Position's
field order -- an implementation choice, not a rulebook mandate (docs/tasks.md
Sec. 3.2.2 only requires both sides agree on origin corner and start index,
not on array ordering).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

from police_thief.domain.board import BoardConfig, Position
from police_thief.domain.scent import ScentConfig
from police_thief.domain.scoring import ScoringTable
from police_thief.services.commit_reveal import canonical_json
from police_thief.shared.config import ConfigError

MIN_MAX_BARRIERS = 14
MIN_GRID_SIZE = 7
SUPPORTED_SCHEMA_VERSIONS = frozenset({"1.00"})
_FIXED_SCENT_CONFIG = ScentConfig()  # docs/tasks.md Sec. 4.2: fixed, not a minimum floor


class GameConfigError(ConfigError):
    """Raised when the shared match config is missing, malformed, or below floor."""


@dataclass(frozen=True)
class MatchParameters:
    """Everything Chapter 3's board/scoring logic needs for one match."""

    board: BoardConfig
    scoring: ScoringTable
    scent: ScentConfig
    thief_start: Position
    cop_start: Position
    max_moves: int
    survival_threshold: int


def _validate_fixed_scent_config(scent: ScentConfig, path: Path) -> None:
    """Sec. 4.2: scent parameters are FIXED, not team-negotiable minimums."""
    fixed = _FIXED_SCENT_CONFIG
    if not math.isclose(scent.center_intensity, fixed.center_intensity):
        raise GameConfigError(
            f"scent_center_intensity must be exactly {fixed.center_intensity} at {path}"
        )
    if not math.isclose(scent.decay_rate, fixed.decay_rate):
        raise GameConfigError(f"scent_decay_rate must be exactly {fixed.decay_rate} at {path}")
    if scent.field_size != fixed.field_size:
        raise GameConfigError(f"scent_field_size must be exactly {fixed.field_size} at {path}")


def config_fingerprint(path: Path) -> str:
    """SHA-256 over the canonically-serialized shared config (Sec. 4.2.6/5.5).

    "Cryptographically locking" the physics/scent parameters before match
    start means: this fingerprint goes into the signed Step-0 declaration
    (services/step0.py), so any later divergence -- including a change to
    the otherwise-fixed scent parameters -- is detectable by comparing
    fingerprints, without needing a bespoke locking mechanism per section.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return hashlib.sha256(canonical_json(data)).hexdigest()


def load_match_parameters(path: Path) -> MatchParameters:
    """Parse config/game.json into board, scoring, and start-position data."""
    if not path.is_file():
        raise GameConfigError(f"missing shared match config: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        schema_version = str(data["schema_version"])
        if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise GameConfigError(
                f"unsupported schema_version {schema_version!r} at {path}; "
                f"supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
            )
        board_section = data["board_and_agents"]
        movement_section = data["movement_and_barriers"]
        scoring_section = data["scoring"]
        pheromones_section = data["pheromones"]

        grid_size = int(board_section["grid_size"])
        max_barriers = int(movement_section["max_barriers"])
        if grid_size < MIN_GRID_SIZE:
            raise GameConfigError(f"grid_size {grid_size} is below the mandatory floor {MIN_GRID_SIZE}")
        if max_barriers < MIN_MAX_BARRIERS:
            raise GameConfigError(f"max_barriers {max_barriers} is below the mandatory floor {MIN_MAX_BARRIERS}")

        board = BoardConfig(
            grid_size=grid_size,
            axis_origin_corner=str(board_section["axis_origin_corner"]),
            axis_start_index=int(board_section["axis_start_index"]),
            max_barriers=max_barriers,
        )
        scoring = ScoringTable(
            capture_cop=int(scoring_section["capture_cop"]),
            capture_thief=int(scoring_section["capture_thief"]),
            survival_cop=int(scoring_section["survival_cop"]),
            survival_thief=int(scoring_section["survival_thief"]),
            tie_score=int(scoring_section["tie_score"]),
            technical_loss=int(scoring_section["technical_loss"]),
        )
        scent = ScentConfig(
            center_intensity=float(pheromones_section["scent_center_intensity"]),
            decay_rate=float(pheromones_section["scent_decay_rate"]),
            field_size=int(pheromones_section["scent_field_size"]),
        )
        _validate_fixed_scent_config(scent, path)
        return MatchParameters(
            board=board,
            scoring=scoring,
            scent=scent,
            thief_start=Position(*board_section["thief_start"]),
            cop_start=Position(*board_section["cop_start"]),
            max_moves=int(movement_section["max_moves"]),
            survival_threshold=int(movement_section["survival_threshold"]),
        )
    except GameConfigError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise GameConfigError(f"malformed shared config at {path}: {exc}") from exc
