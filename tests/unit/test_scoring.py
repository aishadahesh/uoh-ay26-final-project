"""Unit tests for the scoring table and reward function (Chapter 3, Table 2)."""

import pytest

from police_thief.domain.scoring import MatchOutcome, ScoringTable, score_for


def test_scoring_table_defaults_match_mandatory_parameters_table():
    scoring = ScoringTable()
    assert scoring.capture_cop == 20
    assert scoring.capture_thief == 5
    assert scoring.survival_cop == 5
    assert scoring.survival_thief == 10
    assert scoring.tie_score == 2
    assert scoring.technical_loss == 0


def test_score_for_capture_favors_the_cop():
    scoring = ScoringTable()
    assert score_for(MatchOutcome.CAPTURE, scoring) == (20, 5)


def test_score_for_survival_favors_the_thief():
    scoring = ScoringTable()
    assert score_for(MatchOutcome.SURVIVAL, scoring) == (5, 10)


def test_score_for_technical_loss_zeroes_both_sides():
    scoring = ScoringTable()
    assert score_for(MatchOutcome.TECHNICAL_LOSS, scoring) == (0, 0)


def test_score_for_tie_awards_both_sides_equally():
    scoring = ScoringTable()
    assert score_for(MatchOutcome.TIE, scoring) == (2, 2)


def test_scoring_values_can_be_raised_via_config_without_code_changes():
    scoring = ScoringTable(capture_cop=100)
    assert score_for(MatchOutcome.CAPTURE, scoring) == (100, 5)


def test_score_for_rejects_an_unhandled_outcome():
    with pytest.raises(ValueError):
        score_for("not-a-real-outcome", ScoringTable())  # type: ignore[arg-type]
