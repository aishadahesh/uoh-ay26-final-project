"""Unit tests for the Chapter-1 Dec-POMDP formal scaffolding."""

import pytest

from police_thief.domain.dec_pomdp import (
    DecPOMDPSpec,
    DiscountFactorError,
    validate_discount_factor,
)
from police_thief.shared.constants import NUM_AGENTS, AgentRole


def test_num_agents_is_fixed_at_two():
    assert NUM_AGENTS == 2


def test_agent_role_has_exactly_cop_and_thief():
    assert {role.value for role in AgentRole} == {"cop", "thief"}


@pytest.mark.parametrize("gamma", [0.0, 0.5, 0.9, 0.999999])
def test_validate_discount_factor_accepts_valid_range(gamma):
    assert validate_discount_factor(gamma) == gamma


@pytest.mark.parametrize("gamma", [-0.1, 1.0, 1.5, -1.0])
def test_validate_discount_factor_rejects_out_of_range(gamma):
    with pytest.raises(DiscountFactorError):
        validate_discount_factor(gamma)


def test_dec_pomdp_spec_defaults_are_valid():
    spec = DecPOMDPSpec()
    assert spec.num_agents == 2
    assert spec.discount_factor == 0.0


def test_dec_pomdp_spec_rejects_wrong_agent_count():
    with pytest.raises(ValueError):
        DecPOMDPSpec(num_agents=3)


def test_dec_pomdp_spec_rejects_invalid_discount_factor():
    with pytest.raises(DiscountFactorError):
        DecPOMDPSpec(discount_factor=1.0)


def test_dec_pomdp_spec_is_immutable():
    spec = DecPOMDPSpec()
    with pytest.raises(AttributeError):
        spec.discount_factor = 0.5  # type: ignore[misc]
