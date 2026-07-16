"""CLI entry point: `uv run python -m police_thief <command> ...`.

Commands:
  serve --role cop|thief   Start this peer's FastMCP server (Chapter 2).
  simulate                 Run a single-process local match with placeholder
                           policies and print the result (Chapter 3).
  replay --log-file PATH   Launch the Replay Viewer against a saved match
                           log (Chapter 7) -- runs standalone, independent
                           of any live match code (docs/tasks.md T0437).

`serve` is the concrete realization of Chapter 2's "Total Separation of
Working Environments" rule: one shared codebase (docs/PLAN.md ADR-011), but
each invocation is its own OS process reading only its own role's config,
sharing no memory with the other role's process. `simulate` has no
networking or role concept at all -- it exercises board/movement/barrier/
capture/scoring end-to-end against the single shared config/game.json.
"""

from __future__ import annotations

import argparse
import tkinter as tk
from pathlib import Path

from police_thief.domain.replay import ReplaySession, load_log
from police_thief.domain.simulation import run_local_match
from police_thief.gui.replay_gui import ReplayGUI
from police_thief.services.mcp_server import build_peer_server, run_peer_server
from police_thief.shared.config import load_network_config
from police_thief.shared.constants import AgentRole
from police_thief.shared.game_config import load_match_parameters

DEFAULT_CONFIG_ROOT = Path(__file__).resolve().parents[2] / "config"
DEFAULT_GAME_CONFIG = DEFAULT_CONFIG_ROOT / "game.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the `serve`/`simulate`/`replay` subcommands and their options."""
    parser = argparse.ArgumentParser(prog="police_thief")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve = subparsers.add_parser("serve", help="Start this peer's FastMCP server")
    serve.add_argument("--role", required=True, choices=[role.value for role in AgentRole])
    serve.add_argument("--config-root", type=Path, default=DEFAULT_CONFIG_ROOT)

    simulate = subparsers.add_parser("simulate", help="Run a local placeholder-policy match")
    simulate.add_argument("--game-config", type=Path, default=DEFAULT_GAME_CONFIG)

    replay = subparsers.add_parser("replay", help="Launch the Replay Viewer on a saved match log")
    replay.add_argument("--log-file", required=True, type=Path)

    return parser.parse_args(argv)


def _serve(args: argparse.Namespace) -> None:
    role = AgentRole(args.role)
    network = load_network_config(role, args.config_root)
    mcp = build_peer_server(peer_name=f"{role.value}_peer")
    run_peer_server(mcp, host="0.0.0.0", port=network.my_port)


def _simulate(args: argparse.Namespace) -> None:
    params = load_match_parameters(args.game_config)
    result = run_local_match(params)
    print(
        f"outcome={result.outcome.value} cop_score={result.cop_score} "
        f"thief_score={result.thief_score} turns_played={result.turns_played}"
    )


def _replay(args: argparse.Namespace) -> None:
    session = ReplaySession(load_log(args.log_file))
    root = tk.Tk()
    root.title(f"Replay Viewer - {args.log_file.name}")
    ReplayGUI(root, session)
    root.mainloop()


def main(argv: list[str] | None = None) -> None:
    """Dispatch to `serve`, `simulate`, or `replay` based on the parsed subcommand."""
    args = parse_args(argv)
    if args.command == "serve":
        _serve(args)
    elif args.command == "simulate":
        _simulate(args)
    elif args.command == "replay":
        _replay(args)


if __name__ == "__main__":
    main()
