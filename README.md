# Bonfire

A real-time, multiplayer campfire website where visitors gather as named knights around a shared animated bonfire. Click the fire to toss colored powder and watch the flames change — your colors are visible to everyone else gathered at the bonfire.

## Features

- **Animated bonfire** — procedural particle system with a warm fire, rising embers, and ambient glow rendered on an HTML5 Canvas
- **Night sky** — twinkling stars and a moon whose phase matches the real current lunar cycle
- **Powder toss** — click the bonfire to throw colored powder into the flames; the fire briefly shifts to your color and sparks fly across the screen
- **Multiplayer presence** — all connected visitors are shown as knight silhouettes around the fire in real time via WebSockets
- **Knight identity** — each visitor is assigned a unique procedurally generated name (e.g. "Siegward the Resolute") and a color, persisted in a cookie for 24 hours
- **Broadcast effects** — powder tosses from any visitor are broadcast to every connected client simultaneously

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | [Quart](https://quart.palletsprojects.com/) (async Flask-compatible) |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) |
| Database | PostgreSQL via [asyncpg](https://github.com/MagicStack/asyncpg) |
| Frontend | Vanilla JavaScript (no frameworks) + HTML5 Canvas |
| Containerization | Docker / Docker Compose |
| Dependency management | [uv](https://github.com/astral-sh/uv) |

## Project Structure

```
bonfire/
├── src/bonfire/          # Python backend package
│   ├── app.py            # Quart application factory
│   ├── config.py         # Configuration (DATABASE_URL, SECRET_KEY, HOST, PORT)
│   ├── db.py             # asyncpg connection pool, schema initialization
│   ├── models.py         # Session dataclass
│   ├── routes.py         # HTTP routes (session cookie assignment, index render)
│   ├── ws.py             # WebSocket handler, in-memory connected-user tracking, broadcast
│   ├── moon.py           # Real-time lunar phase calculation
│   └── names.py          # Procedural knight name generator
├── static/
│   ├── css/style.css     # Global styles
│   └── js/
│       ├── main.js       # Entry point, wires all modules together
│       ├── sky.js        # Canvas renderer: night sky, stars, moon
│       ├── fire.js       # Canvas renderer: fire particle system, powder effect
│       ├── powder.js     # Canvas renderer: powder-toss spark animation
│       ├── knights.js    # DOM management: knight sprites, positioning around fire
│       └── ws.js         # WebSocket client, event emitter
├── templates/
│   └── index.html        # Single-page HTML template
├── tests/                # pytest test suite
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Running Locally

### With Docker Compose (recommended)

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`.

### Without Docker

Requires Python 3.12+ and a running PostgreSQL instance.

```bash
# Install dependencies
uv sync

# Set environment variable
export DATABASE_URL=postgresql://bonfire:bonfire@localhost:5432/bonfire

# Run the server
uv run uvicorn bonfire.app:create_app --factory --host 0.0.0.0 --port 8000
```

## Configuration

All configuration is read from environment variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://bonfire:bonfire@localhost:5432/bonfire` | PostgreSQL connection string |
| `SECRET_KEY` | `dev-secret-change-me` | Secret key (change in production) |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |

## Running Tests

```bash
uv sync --extra test
uv run pytest
```

## How It Works

1. When a visitor arrives, the server checks for a `session_id` cookie. If none exists, a new session is created in PostgreSQL with a randomly generated knight name, sprite ID, and color index.
2. The page connects to the `/ws` WebSocket endpoint. On connection the server sends an `init` message containing the visitor's identity, all currently connected users, the current moon phase, and the color palette.
3. Other visitors receive a `user_joined` event and their knight silhouette appears around the fire. When they disconnect a `user_left` event removes them.
4. Clicking the bonfire sends a `powder_toss` message over WebSocket. The server broadcasts it to all connected clients, each of whom animates the fire and spark effect in their assigned color.
