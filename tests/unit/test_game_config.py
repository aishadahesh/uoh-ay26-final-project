"""Unit tests for the shared config/game.json loader (Chapter 3)."""

import json
from pathlib import Path

import pytest

from police_thief.domain.board import Position
from police_thief.shared.game_config import GameConfigError, load_match_parameters

VALID_CONFIG: dict = {
    "schema_version": "1.00",
    "agreed_between": ["cop", "thief"],
    "board_and_agents": {
        "grid_size": 7,
        "num_agents": 2,
        "thief_start": [3, 3],
        "cop_start": [0, 0],
        "axis_origin_corner": "top-left",
        "axis_start_index": 0,
    },
    "movement_and_barriers": {
        "move_set": ["N", "S", "E", "W", "STAY"],
        "max_barriers": 14,
        "max_moves": 35,
        "survival_threshold": 35,
    },
    "scoring": {
        "capture_cop": 20,
        "capture_thief": 5,
        "survival_cop": 5,
        "survival_thief": 10,
        "tie_score": 2,
        "technical_loss": 0,
    },
}


def _write(tmp_path, data: dict):
    path = tmp_path / "game.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_match_parameters_reads_the_real_shipped_config():
    params = load_match_parameters(Path("config/game.json"))
    assert params.board.grid_size == 7
    assert params.cop_start == Position(0, 0)
    assert params.thief_start == Position(3, 3)


def test_load_match_parameters_parses_a_valid_config(tmp_path):
    params = load_match_parameters(_write(tmp_path, VALID_CONFIG))
    assert params.board.grid_size == 7
    assert params.board.max_barriers == 14
    assert params.scoring.capture_cop == 20
    assert params.max_moves == 35
    assert params.survival_threshold == 35


def test_load_match_parameters_raises_on_missing_file(tmp_path):
    with pytest.raises(GameConfigError, match="missing shared match config"):
        load_match_parameters(tmp_path / "does_not_exist.json")


def test_load_match_parameters_raises_on_missing_section(tmp_path):
    broken = {k: v for k, v in VALID_CONFIG.items() if k != "scoring"}
    with pytest.raises(GameConfigError, match="malformed shared config"):
        load_match_parameters(_write(tmp_path, broken))


def test_load_match_parameters_rejects_grid_size_below_floor(tmp_path):
    data = json.loads(json.dumps(VALID_CONFIG))
    data["board_and_agents"]["grid_size"] = 5
    with pytest.raises(GameConfigError, match="below the mandatory floor"):
        load_match_parameters(_write(tmp_path, data))


def test_load_match_parameters_rejects_unsupported_schema_version(tmp_path):
    data = json.loads(json.dumps(VALID_CONFIG))
    data["schema_version"] = "99.99"
    with pytest.raises(GameConfigError, match="unsupported schema_version"):
        load_match_parameters(_write(tmp_path, data))


def test_load_match_parameters_rejects_max_barriers_below_floor(tmp_path):
    data = json.loads(json.dumps(VALID_CONFIG))
    data["movement_and_barriers"]["max_barriers"] = 5
    with pytest.raises(GameConfigError, match="below the mandatory floor"):
        load_match_parameters(_write(tmp_path, data))
