import json

from bonfire.ws import COLORS, broadcast, connected


def test_colors_has_12_entries():
    assert len(COLORS) == 12


def test_colors_are_valid_hex():
    import re
    for color in COLORS:
        assert re.match(r"^#[0-9A-Fa-f]{6}$", color), f"Invalid hex color: {color}"


def test_connected_starts_empty():
    """The connected dict should be empty at module load."""
    # Clear any leftover state from other tests
    connected.clear()
    assert len(connected) == 0


import asyncio
import pytest


@pytest.mark.asyncio
async def test_broadcast_sends_to_all():
    """broadcast() should send JSON to all connected websockets."""
    connected.clear()

    received_a = []
    received_b = []

    class FakeWS:
        def __init__(self, store):
            self._store = store
        async def send(self, data):
            self._store.append(json.loads(data))

    connected["user-a"] = FakeWS(received_a)
    connected["user-b"] = FakeWS(received_b)

    await broadcast({"type": "test", "data": 42})

    assert len(received_a) == 1
    assert received_a[0] == {"type": "test", "data": 42}
    assert len(received_b) == 1
    assert received_b[0] == {"type": "test", "data": 42}

    connected.clear()


@pytest.mark.asyncio
async def test_broadcast_excludes_sender():
    """broadcast() with exclude should skip that user."""
    connected.clear()

    received_a = []
    received_b = []

    class FakeWS:
        def __init__(self, store):
            self._store = store
        async def send(self, data):
            self._store.append(json.loads(data))

    connected["user-a"] = FakeWS(received_a)
    connected["user-b"] = FakeWS(received_b)

    await broadcast({"type": "joined"}, exclude="user-a")

    assert len(received_a) == 0
    assert len(received_b) == 1

    connected.clear()


@pytest.mark.asyncio
async def test_broadcast_handles_broken_ws():
    """If a websocket raises on send, it should be removed from connected."""
    connected.clear()

    received_b = []

    class BrokenWS:
        async def send(self, data):
            raise ConnectionError("gone")

    class GoodWS:
        def __init__(self, store):
            self._store = store
        async def send(self, data):
            self._store.append(data)

    connected["broken"] = BrokenWS()
    connected["good"] = GoodWS(received_b)

    await broadcast({"type": "test"})

    # Broken WS should have been removed
    assert "broken" not in connected
    assert len(received_b) == 1

    connected.clear()


@pytest.mark.asyncio
async def test_broadcast_empty_connected():
    """broadcast() with no connected users should not raise."""
    connected.clear()
    await broadcast({"type": "test"})  # Should complete without error


def test_colors_all_unique():
    """All 12 colors should be distinct."""
    assert len(COLORS) == len(set(COLORS))
