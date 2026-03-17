import random
import uuid

from quart import Blueprint, make_response, render_template, request

from . import db
from .names import generate_knight_name

bp = Blueprint("routes", __name__)

COLOR_COUNT = 12


@bp.route("/")
async def index():
    session_id = request.cookies.get("session_id")
    new_cookie = False

    if session_id:
        try:
            session_id = uuid.UUID(session_id)
        except ValueError:
            session_id = None

    if session_id and db.pool:
        row = await db.pool.fetchrow(
            "SELECT id, knight_name, sprite_id, color_index FROM bonfire_sessions WHERE id = $1",
            session_id,
        )
        if row:
            await db.pool.execute(
                "UPDATE bonfire_sessions SET last_seen = now() WHERE id = $1", session_id
            )
        else:
            session_id = None

    if not session_id:
        session_id = uuid.uuid4()
        knight_name = generate_knight_name()
        sprite_id = random.randint(1, 5)
        color_index = random.randint(0, COLOR_COUNT - 1)
        new_cookie = True
        if db.pool:
            await db.pool.execute(
                """INSERT INTO bonfire_sessions (id, knight_name, sprite_id, color_index)
                   VALUES ($1, $2, $3, $4)""",
                session_id, knight_name, sprite_id, color_index,
            )

    body = await render_template("index.html")
    resp = await make_response(body)

    if new_cookie:
        resp.set_cookie(
            "session_id",
            str(session_id),
            max_age=86400,
            httponly=True,
            samesite="Lax",
        )

    return resp
