"""CLI entry point: `uv run python -m police_thief --role cop|thief`.

Starts this peer's FastMCP server bound to 0.0.0.0 on its configured port,
loading configuration only from this role's own config/<role>/ directory.
This is the concrete realization of Chapter 2's "Total Separation of Working
Environments" rule: one shared codebase (see docs/PLAN.md ADR-011), but each
invocation is its own OS process reading only its own config, sharing no
memory with the other role's process.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from police_thief.services.mcp_server import build_peer_server, run_peer_server
from police_thief.shared.config import load_network_config
from police_thief.shared.constants import AgentRole

DEFAULT_CONFIG_ROOT = Path(__file__).resolve().parents[2] / "config"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse `--role` (required) and `--config-root` (optional override)."""
    parser = argparse.ArgumentParser(prog="police_thief")
    parser.add_argument("--role", required=True, choices=[role.value for role in AgentRole])
    parser.add_argument("--config-root", type=Path, default=DEFAULT_CONFIG_ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Load this role's config and run its FastMCP server until interrupted."""
    args = parse_args(argv)
    role = AgentRole(args.role)
    network = load_network_config(role, args.config_root)
    mcp = build_peer_server(peer_name=f"{role.value}_peer")
    run_peer_server(mcp, host="0.0.0.0", port=network.my_port)


if __name__ == "__main__":
    main()
