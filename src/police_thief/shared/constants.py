"""Immutable project constants.

Only true constants live here: physical/mathematical constants, enum
values, and parameter defaults that are never meant to be retuned per
match. Anything a team or a match negotiation could plausibly want to
change belongs in config/game.json or config/game.toml instead — see
docs/tasks.md Appendix B and the "no embedded values in code" rule in
ref/software_submission_guidelines-V3.pdf Sec. 7.2.
"""

from enum import StrEnum


class AgentRole(StrEnum):
    """The two — and only two — decision-makers in the Dec-POMDP.

    n = 2 is fixed by the rulebook (docs/tasks.md Chapter 1, Sec. 2); this
    enum is the single, typed vocabulary for "which side am I" used by
    every later module (CLI role flag, config directory selection, log
    file naming, etc.) instead of ad hoc string literals.
    """

    COP = "cop"
    THIEF = "thief"


NUM_AGENTS = 2
"""n in the Dec-POMDP tuple <n, S, {A_i}, P, R, {Omega_i}, O, gamma>.

Fixed at 2 for this project (one cop, one thief) — never validated as
"at least 2", always exactly 2. See DecPOMDPSpec in
police_thief.domain.dec_pomdp for the enforcement point.
"""
