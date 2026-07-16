"""Unit tests for the Step-0 computational-fairness declaration (Chapter 5)."""

import platform
import subprocess
from dataclasses import replace
from unittest.mock import mock_open, patch

import pytest

from police_thief.services.step0 import (
    GitCommitHashError,
    HardwareSpec,
    Step0Declaration,
    TokenUsage,
    _detect_ram_gb,
    gather_hardware_spec,
    get_git_commit_hash,
    sign_step0,
    verify_step0_signature,
)


def test_get_git_commit_hash_returns_a_40_character_sha1_in_this_real_repo():
    commit_hash = get_git_commit_hash()
    assert len(commit_hash) == 40
    assert all(ch in "0123456789abcdef" for ch in commit_hash)


def test_get_git_commit_hash_raises_outside_a_git_repository(tmp_path):
    with pytest.raises(GitCommitHashError):
        get_git_commit_hash(cwd=str(tmp_path))


def test_gather_hardware_spec_reports_a_positive_cpu_count():
    hw = gather_hardware_spec(llm_model="template")
    assert hw.cpu_count > 0
    assert hw.os_name == platform.system()
    assert hw.llm_model == "template"
    assert hw.gpu_present is False


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific RAM detection path")
def test_gather_hardware_spec_detects_positive_ram_on_windows():
    hw = gather_hardware_spec(llm_model="template")
    assert hw.ram_gb > 0.0


def test_detect_ram_gb_parses_proc_meminfo_on_linux():
    """Mocked: this dev machine is Windows, but the Linux parsing logic
    (/proc/meminfo's MemTotal line, reported in kB) is still testable.
    """
    fake_meminfo = "MemTotal:       16777216 kB\nMemFree:         1000000 kB\n"
    with (
        patch("platform.system", return_value="Linux"),
        patch("builtins.open", mock_open(read_data=fake_meminfo)),
    ):
        assert _detect_ram_gb() == pytest.approx(16.0, abs=0.01)


def test_detect_ram_gb_parses_sysctl_on_macos():
    fake_result = subprocess.CompletedProcess(args=[], returncode=0, stdout=str(16 * 1024**3))
    with (
        patch("platform.system", return_value="Darwin"),
        patch("subprocess.run", return_value=fake_result),
    ):
        assert _detect_ram_gb() == pytest.approx(16.0, abs=0.01)


def test_detect_ram_gb_falls_back_to_zero_on_any_detection_failure():
    with patch("platform.system", side_effect=RuntimeError("boom")):
        assert _detect_ram_gb() == 0.0


def test_detect_ram_gb_falls_back_to_zero_on_unrecognized_platform():
    with patch("platform.system", return_value="PlayStation5"):
        assert _detect_ram_gb() == 0.0


def _make_declaration(**overrides) -> Step0Declaration:
    defaults = {
        "hardware": HardwareSpec(
            os_name="Windows", cpu_count=8, ram_gb=16.0, gpu_present=False, llm_model="template"
        ),
        "code_version": "1.00",
        "team_name": "test-team",
        "game_id": "g1",
        "sub_game_number": 1,
        "git_commit_hash": "a" * 40,
        "config_fingerprint": "b" * 64,
    }
    defaults.update(overrides)
    return Step0Declaration(**defaults)


def test_sign_step0_verifies_correctly_with_the_right_key():
    declaration = _make_declaration()
    signed = sign_step0(declaration, shared_key=b"shared-secret")
    assert verify_step0_signature(signed, shared_key=b"shared-secret")


def test_sign_step0_fails_verification_with_the_wrong_key():
    declaration = _make_declaration()
    signed = sign_step0(declaration, shared_key=b"shared-secret")
    assert not verify_step0_signature(signed, shared_key=b"wrong-key")


def test_sign_step0_fails_verification_if_declaration_is_altered_after_signing():
    declaration = _make_declaration()
    signed = sign_step0(declaration, shared_key=b"shared-secret")
    tampered = replace(signed, declaration=replace(declaration, team_name="evil-team"))
    assert not verify_step0_signature(tampered, shared_key=b"shared-secret")


def test_sign_step0_fails_verification_if_nested_hardware_spec_is_altered():
    declaration = _make_declaration()
    signed = sign_step0(declaration, shared_key=b"shared-secret")
    tampered_hw = replace(declaration.hardware, ram_gb=9999.0)
    tampered = replace(signed, declaration=replace(declaration, hardware=tampered_hw))
    assert not verify_step0_signature(tampered, shared_key=b"shared-secret")


def test_token_usage_accumulates_across_multiple_calls():
    usage = TokenUsage()
    usage.add(input_tokens=100, output_tokens=50)
    usage.add(input_tokens=10, output_tokens=5)
    assert usage.input_tokens == 110
    assert usage.output_tokens == 55
    assert usage.total == 165


def test_token_usage_starts_at_zero():
    usage = TokenUsage()
    assert usage.total == 0
