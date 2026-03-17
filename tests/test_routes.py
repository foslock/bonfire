import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bonfire.app import create_app


@pytest.fixture
def app():
    """Create app with DB hooks disabled (no real Postgres needed)."""
    app = create_app()
    # Remove the before/after serving hooks that connect to Postgres
    app.before_serving_funcs = []
    app.after_serving_funcs = []
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.asyncio
async def test_index_returns_200(client):
    """GET / should return 200 with HTML content."""
    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = None  # No DB connection
        resp = await client.get("/")
    assert resp.status_code == 200
    data = await resp.get_data(as_text=True)
    assert "<html" in data.lower()


@pytest.mark.asyncio
async def test_index_sets_session_cookie(client):
    """First visit should set a session_id cookie."""
    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = None
        resp = await client.get("/")
    cookies = resp.headers.getlist("Set-Cookie")
    cookie_str = "; ".join(cookies)
    assert "session_id=" in cookie_str


@pytest.mark.asyncio
async def test_index_cookie_is_valid_uuid(client):
    """The session_id cookie should be a valid UUID."""
    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = None
        resp = await client.get("/")
    cookies = resp.headers.getlist("Set-Cookie")
    cookie_str = "; ".join(cookies)
    # Extract the UUID value
    for part in cookie_str.split(";"):
        part = part.strip()
        if part.startswith("session_id="):
            val = part.split("=", 1)[1]
            uuid.UUID(val)  # Raises if invalid
            break
    else:
        pytest.fail("session_id cookie not found")


@pytest.mark.asyncio
async def test_index_cookie_is_httponly(client):
    """Session cookie should be HttpOnly for security."""
    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = None
        resp = await client.get("/")
    cookies = resp.headers.getlist("Set-Cookie")
    cookie_str = "; ".join(cookies)
    assert "HttpOnly" in cookie_str


@pytest.mark.asyncio
async def test_index_contains_required_elements(client):
    """Page should contain key DOM elements for the bonfire scene."""
    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = None
        resp = await client.get("/")
    html = await resp.get_data(as_text=True)
    assert 'id="sky-canvas"' in html
    assert 'id="fire-canvas"' in html
    assert 'id="bonfire-area"' in html
    assert 'id="knights-container"' in html
    assert 'id="powder-canvas"' in html
    assert 'id="hud"' in html
    assert 'id="my-name"' in html


@pytest.mark.asyncio
async def test_index_loads_all_js_modules(client):
    """Page should include script tags for all JS modules."""
    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = None
        resp = await client.get("/")
    html = await resp.get_data(as_text=True)
    for module in ["ws.js", "sky.js", "fire.js", "knights.js", "powder.js", "main.js"]:
        assert module in html, f"Missing script tag for {module}"


@pytest.mark.asyncio
async def test_index_with_db_creates_session(client):
    """When DB is available, visiting / should INSERT a session row."""
    mock_pool = AsyncMock()
    mock_pool.fetchrow = AsyncMock(return_value=None)
    mock_pool.execute = AsyncMock()

    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = mock_pool
        resp = await client.get("/")

    assert resp.status_code == 200
    # Should have called execute to INSERT the new session
    mock_pool.execute.assert_called_once()
    call_args = mock_pool.execute.call_args
    assert "INSERT INTO sessions" in call_args[0][0]


@pytest.mark.asyncio
async def test_index_existing_session_touches_last_seen(client):
    """Returning with a valid session cookie should UPDATE last_seen."""
    session_id = uuid.uuid4()
    mock_pool = AsyncMock()
    mock_pool.fetchrow = AsyncMock(return_value={
        "id": session_id,
        "knight_name": "Solaire the Brave",
        "sprite_id": 3,
        "color_index": 0,
    })
    mock_pool.execute = AsyncMock()

    with patch("bonfire.routes.db") as mock_db:
        mock_db.pool = mock_pool
        resp = await client.get("/", headers={
            "Cookie": f"session_id={session_id}"
        })

    assert resp.status_code == 200
    # Should have called execute for UPDATE last_seen
    mock_pool.execute.assert_called_once()
    call_args = mock_pool.execute.call_args
    assert "UPDATE sessions SET last_seen" in call_args[0][0]


@pytest.mark.asyncio
async def test_static_css_accessible(client):
    """CSS file should be accessible."""
    resp = await client.get("/static/css/style.css")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_static_js_accessible(client):
    """JS files should be accessible."""
    for js in ["ws.js", "sky.js", "fire.js", "knights.js", "powder.js", "main.js"]:
        resp = await client.get(f"/static/js/{js}")
        assert resp.status_code == 200, f"Failed to serve {js}"
