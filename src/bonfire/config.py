import os


class Config:
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "postgresql://bonfire:bonfire@localhost:5432/bonfire"
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8000"))
