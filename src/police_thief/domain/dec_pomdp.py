"""Formal Dec-POMDP scaffolding for the Cops-and-Robbers game (Chapter 1).

docs/tasks.md Chapter 1 models the match as a Decentralized Partially
Observable Markov Decision Process:

    <n, S, {A_i}, P, R, {Omega_i}, O, gamma>

This module does not implement the board, the transition function, or the
reward table — those are concrete, chapter-specific concerns built in later
stages:

    - S (state space)              -> police_thief.domain.board       (Chapter 3)
    - {A_i} (action spaces)         -> police_thief.domain.board       (Chapter 3)
    - P (transition function)       -> the game engine's turn resolution (Chapter 3)
    - R (reward function)           -> police_thief.domain.scoring     (Chapter 3)
    - {Omega_i}, O (observations)   -> police_thief.domain.scent/belief (Chapter 4)

Encoding those six components as data here, before the board exists, would
either be a meaningless stub or force premature coupling to Chapter 3's
design. What *does* belong at the framework level, and is implemented here,
is the shared, validated, typed vocabulary every later module conforms to:
how many agents there are, and how the discount horizon is defined and
validated.
"""

from __future__ import annotations

from dataclasses import dataclass

from police_thief.shared.constants import NUM_AGENTS


class DiscountFactorError(ValueError):
    """Raised when a discount factor gamma falls outside its valid domain."""


def validate_discount_factor(gamma: float) -> float:
    """Validate gamma against the Dec-POMDP tuple's domain: 0 <= gamma < 1.

    A gamma near 1 rewards long-horizon strategic patience (e.g. building a
    barrier trap over many turns before it pays off); a gamma near 0 makes
    the agent short-sighted, valuing only the immediate reward. See
    docs/tasks.md Chapter 1, Sec. 2 (table row for gamma).
    """
    if not (0.0 <= gamma < 1.0):
        raise DiscountFactorError(f"discount factor must satisfy 0 <= gamma < 1, got {gamma!r}")
    return gamma


@dataclass(frozen=True)
class DecPOMDPSpec:
    """The two framework-level components of the eight-component tuple.

    Deliberately small: `num_agents` and `discount_factor` are the only
    pieces of the Dec-POMDP tuple that are meaningful as standalone data at
    this stage of the project. The remaining six components are concrete
    behaviors, not data, and are implemented across Chapters 3 and 4 (see
    the module docstring above for the exact mapping).
    """

    num_agents: int = NUM_AGENTS
    discount_factor: float = 0.0

    def __post_init__(self) -> None:
        if self.num_agents != NUM_AGENTS:
            raise ValueError(
                f"this project's rulebook fixes num_agents = {NUM_AGENTS}, got {self.num_agents}"
            )
        validate_discount_factor(self.discount_factor)
