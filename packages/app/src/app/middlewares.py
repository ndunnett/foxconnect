from typing import Any

from quart import Quart, session


def init_app(app: Quart) -> None:
    @app.context_processor
    def foxconnect_context() -> dict[str, Any]:
        return app.config["FOXCONNECT_CONTEXT"]

    @app.before_request
    def make_session_permanent() -> None:
        session.permanent = True
