import asyncio
import asyncpg
from quart import current_app

pool: asyncpg.Pool | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          UUID PRIMARY KEY,
    knight_name TEXT NOT NULL,
    sprite_id   SMALLINT NOT NULL,
    color_index SMALLINT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen   TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


async def init_pool() -> None:
    global pool
    url = current_app.config["DATABASE_URL"]
    for attempt in range(10):
        try:
            pool = await asyncpg.create_pool(url, min_size=2, max_size=10)
            async with pool.acquire() as conn:
                await conn.execute(SCHEMA)
            return
        except (OSError, asyncpg.PostgresError) as exc:
            if attempt == 9:
                raise
            await asyncio.sleep(1)


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None
