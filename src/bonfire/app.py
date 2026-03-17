from pathlib import Path
from quart import Quart

ROOT = Path(__file__).resolve().parent.parent.parent


def create_app() -> Quart:
    app = Quart(
        __name__,
        static_folder=str(ROOT / "static"),
        template_folder=str(ROOT / "templates"),
    )
    app.config.from_object("bonfire.config.Config")

    from . import db
    app.before_serving(db.init_pool)
    app.after_serving(db.close_pool)

    from .routes import bp
    app.register_blueprint(bp)

    from .ws import ws_bp
    app.register_blueprint(ws_bp)

    return app
