"""FastMCP client wrapper: calling the opponent's exposed receive_move tool.

See mcp_server.py's module docstring for the shared design rationale. This
module intentionally does not retry or track deadlines beyond a single
timeout — bounded retries and heartbeat-based failure handling are Chapter
8's Deadline Tracker / Watchdog concern, not this transport-only wrapper's.
"""

from __future__ import annotations

import asyncio

from fastmcp import Client


class PeerClientError(RuntimeError):
    """Raised when a call to the opponent's server fails or times out."""


async def send_move_async(
    opponent_url: str, signed_move: str, signature: str, timeout: float
) -> dict:
    """Call the opponent's receive_move tool and return its response payload."""
    try:
        async with Client(opponent_url, timeout=timeout) as client:
            result = await client.call_tool(
                "receive_move", {"signed_move": signed_move, "signature": signature}
            )
    except Exception as exc:
        raise PeerClientError(f"failed to reach opponent at {opponent_url}: {exc}") from exc
    return result.data


def send_move(opponent_url: str, signed_move: str, signature: str, timeout: float = 10.0) -> dict:
    """Synchronous convenience wrapper around send_move_async."""
    return asyncio.run(send_move_async(opponent_url, signed_move, signature, timeout))
