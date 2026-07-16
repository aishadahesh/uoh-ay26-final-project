"""Unit tests for the legal match state machine (Chapter 8, Sec. 8.2)."""

import pytest

from police_thief.services.state_machine import (
    IllegalStateTransitionError,
    MatchState,
    MatchStateMachine,
)


def test_initial_state_is_waiting_for_opponent():
    sm = MatchStateMachine()
    assert sm.state == MatchState.WAITING_FOR_OPPONENT


def test_full_legal_cycle_returns_to_waiting_for_opponent():
    sm = MatchStateMachine()
    sm.transition(MatchState.COMPUTING_MOVE)
    sm.transition(MatchState.COMMITTING)
    sm.transition(MatchState.AWAITING_REVEAL)
    sm.transition(MatchState.VERIFYING)
    sm.transition(MatchState.WAITING_FOR_OPPONENT)
    assert sm.state == MatchState.WAITING_FOR_OPPONENT


@pytest.mark.parametrize(
    ("start", "target"),
    [
        (MatchState.WAITING_FOR_OPPONENT, MatchState.COMMITTING),
        (MatchState.WAITING_FOR_OPPONENT, MatchState.VERIFYING),
        (MatchState.COMPUTING_MOVE, MatchState.AWAITING_REVEAL),
        (MatchState.COMMITTING, MatchState.WAITING_FOR_OPPONENT),
        (MatchState.VERIFYING, MatchState.COMPUTING_MOVE),
    ],
)
def test_illegal_transitions_are_rejected_immediately(start, target):
    sm = MatchStateMachine(initial=start)
    with pytest.raises(IllegalStateTransitionError):
        sm.transition(target)
    assert sm.state == start  # rejected transition never mutates state


@pytest.mark.parametrize(
    "start",
    [
        MatchState.COMPUTING_MOVE,
        MatchState.COMMITTING,
        MatchState.AWAITING_REVEAL,
        MatchState.VERIFYING,
    ],
)
def test_technical_loss_is_reachable_from_every_non_terminal_state(start):
    sm = MatchStateMachine(initial=start)
    sm.transition(MatchState.TECHNICAL_LOSS)
    assert sm.state == MatchState.TECHNICAL_LOSS


def test_technical_loss_is_terminal_no_legal_transitions_out():
    sm = MatchStateMachine(initial=MatchState.TECHNICAL_LOSS)
    assert sm.is_terminal is True
    assert sm.legal_next_states() == frozenset()
    for target in MatchState:
        with pytest.raises(IllegalStateTransitionError):
            sm.transition(target)


def test_non_terminal_states_are_not_terminal():
    for state in (
        MatchState.WAITING_FOR_OPPONENT,
        MatchState.COMPUTING_MOVE,
        MatchState.COMMITTING,
        MatchState.AWAITING_REVEAL,
        MatchState.VERIFYING,
    ):
        assert MatchStateMachine(initial=state).is_terminal is False


def test_legal_next_states_reflects_the_table_exactly():
    sm = MatchStateMachine(initial=MatchState.COMPUTING_MOVE)
    assert sm.legal_next_states() == frozenset({MatchState.COMMITTING, MatchState.TECHNICAL_LOSS})
