"""Per-peer configuration loading.

Chapter 2's mandatory environment-separation rule (docs/tasks.md Sec. 3,
"Total Separation of Working Environments") requires each role to load its
own config directory (config/police/ vs config/thief/) — never a config
shared in memory with the other role. This module loads only the [network]
section needed for Chapter 2; the fuller shared, signed config/game.json
format (App. B) is introduced once Chapter 3's board parameters exist.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from police_thief.shared.constants import AgentRole


class ConfigError(ValueError):
    """Raised when a per-peer config file is missing or malformed."""


@dataclass(frozen=True)
class NetworkConfig:
    """The [network] section of a role's private config/<role>/game.toml."""

    my_port: int
    opponent_url: str
    turn_timeout_seconds: float


def config_dir_for(role: AgentRole, config_root: Path) -> Path:
    """Return this role's own config directory (config/police/ or config/thief/)."""
    return config_root / role.value


def load_network_config(role: AgentRole, config_root: Path) -> NetworkConfig:
    """Load role's private config/<role>/game.toml [network] section.

    Never reads the other role's directory — the caller passes only its own
    `role`, and this function only ever looks inside that one directory.
    """
    path = config_dir_for(role, config_root) / "game.toml"
    if not path.is_file():
        raise ConfigError(f"missing per-peer config file: {path}")
    with path.open("rb") as f:
        data = tomllib.load(f)
    try:
        network = data["network"]
        return NetworkConfig(
            my_port=int(network["my_port"]),
            opponent_url=str(network["opponent_url"]),
            turn_timeout_seconds=float(network.get("turn_timeout_seconds", 30.0)),
        )
    except KeyError as exc:
        raise ConfigError(f"malformed config at {path}: missing key {exc}") from exc
