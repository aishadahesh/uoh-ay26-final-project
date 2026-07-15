"""Unit tests for the Chapter-2 FastMCP server wrapper (in-memory transport)."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from police_thief.services.mcp_server import MoveEnvelope, build_peer_server


def test_move_envelope_valid_when_both_fields_non_empty():
    envelope = MoveEnvelope(signed_move="N", signature="abc123")
    assert envelope.is_structurally_valid()


@pytest.mark.parametrize(
    ("signed_move", "signature"),
    [("", "abc123"), ("N", ""), ("   ", "abc123"), ("N", "   "), ("", "")],
)
def test_move_envelope_invalid_when_a_field_is_blank(signed_move, signature):
    envelope = MoveEnvelope(signed_move=signed_move, signature=signature)
    assert not envelope.is_structurally_valid()


@pytest.mark.asyncio
async def test_receive_move_accepts_well_formed_payload():
    mcp = build_peer_server("test_peer")
    async with Client(mcp) as client:
        result = await client.call_tool(
            "receive_move", {"signed_move": "N", "signature": "abc123"}
        )
    assert result.data == {"accepted": True, "move": "N"}


@pytest.mark.asyncio
async def test_receive_move_rejects_blank_signature():
    mcp = build_peer_server("test_peer")
    async with Client(mcp) as client:
        result = await client.call_tool("receive_move", {"signed_move": "N", "signature": " "})
    assert result.data == {"accepted": False, "move": None}


@pytest.mark.asyncio
async def test_receive_move_rejects_missing_required_field():
    """FastMCP's own pydantic-derived schema rejects this before our code runs."""
    mcp = build_peer_server("test_peer")
    async with Client(mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("receive_move", {"signed_move": "N"})


@pytest.mark.asyncio
async def test_receive_move_rejects_unexpected_extra_field():
    mcp = build_peer_server("test_peer")
    async with Client(mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "receive_move",
                {"signed_move": "N", "signature": "abc123", "extra_field": 1},
            )


def test_build_peer_server_names_the_server_after_the_peer():
    mcp = build_peer_server("cop_peer")
    assert mcp.name == "cop_peer"
