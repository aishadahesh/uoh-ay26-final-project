"""Unit tests for the Chapter-2 FastMCP client wrapper's error handling."""

import pytest

from police_thief.services.mcp_client import PeerClientError, send_move_async


async def test_send_move_raises_peer_client_error_when_opponent_unreachable():
    """No server is listening on this port -- connection should fail fast."""
    with pytest.raises(PeerClientError, match="failed to reach opponent"):
        await send_move_async(
            "http://127.0.0.1:1/mcp", signed_move="N", signature="abc123", timeout=2.0
        )
