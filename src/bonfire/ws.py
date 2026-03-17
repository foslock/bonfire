import json
import uuid

from quart import Blueprint, websocket

from . import db
from .moon import moon_phase

ws_bp = Blueprint("ws", __name__)

# In-memory connected users: session_id_str -> websocket object
connected: dict[str, object] = {}

COLORS = [
    "#FFD700", "#FFFACD", "#4169E1", "#6A0DAD", "#DC143C", "#50C878",
    "#1B0033", "#00FFFF", "#FF6600", "#1A1A2E", "#C0C0C0", "#FF4500",
]


async def broadcast(message: dict, exclude: str | None = None):
    data = json.dumps(message)
    for sid, ws in list(connected.items()):
        if sid != exclude:
            try:
                await ws.send(data)
            except Exception:
                connected.pop(sid, None)


@ws_bp.websocket("/ws")
async def ws_handler():
    session_id_str = websocket.cookies.get("session_id")
    if not session_id_str:
        return

    try:
        session_uuid = uuid.UUID(session_id_str)
    except ValueError:
        return

    if not db.pool:
        return

    row = await db.pool.fetchrow(
        "SELECT id, knight_name, sprite_id, color_index FROM bonfire_sessions WHERE id = $1",
        session_uuid,
    )
    if not row:
        return

    me = {
        "id": session_id_str,
        "name": row["knight_name"],
        "sprite_id": row["sprite_id"],
        "color_index": row["color_index"],
    }

    # Build list of currently connected users
    other_users = []
    for sid in connected:
        try:
            sid_uuid = uuid.UUID(sid)
        except ValueError:
            continue
        other_row = await db.pool.fetchrow(
            "SELECT knight_name, sprite_id FROM bonfire_sessions WHERE id = $1", sid_uuid
        )
        if other_row:
            other_users.append({
                "id": sid,
                "name": other_row["knight_name"],
                "sprite_id": other_row["sprite_id"],
            })

    ws = websocket._get_current_object()
    connected[session_id_str] = ws

    # Send init to this client
    await ws.send(json.dumps({
        "type": "init",
        "you": me,
        "users": other_users,
        "moon_phase": moon_phase(),
        "colors": COLORS,
    }))

    # Broadcast join to others
    await broadcast({
        "type": "user_joined",
        "id": session_id_str,
        "name": row["knight_name"],
        "sprite_id": row["sprite_id"],
    }, exclude=session_id_str)

    try:
        while True:
            raw = await ws.receive()
            try:
                msg = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue

            if msg.get("type") == "powder_toss":
                await broadcast({
                    "type": "powder_toss",
                    "user_id": session_id_str,
                    "color_index": row["color_index"],
                })
    except Exception:
        pass
    finally:
        connected.pop(session_id_str, None)
        await broadcast({
            "type": "user_left",
            "id": session_id_str,
        })
