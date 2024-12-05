from importlib import import_module
from typing import Any

from dotenv import dotenv_values
from quart import Quart, session
from quart_d3graphviz import D3Graphviz
from quart_foxdata import FoxData
from quart_htmx import HTMX


def create_app() -> Quart:
    app = Quart(__name__)
    app.config["FOXCONNECT_CONTEXT"] = {"navbar_links": {}}
    app.config.from_prefixed_env()
    app.config.from_mapping(dotenv_values(".env"))

    # initialise extensions
    for extension_class in (D3Graphviz, FoxData, HTMX):
        extension_class().init_app(app)

    # initialise blueprints
    for module_name in ("main", "blocks", "search"):
        import_module(f"app.{module_name}").init_app(app)

    # add custom context processor
    @app.context_processor
    def foxconnect_context() -> dict[str, Any]:
        return app.config["FOXCONNECT_CONTEXT"]

    # make sessions persistent between browser sessions
    @app.before_request
    def make_session_permanent() -> None:
        session.permanent = True

    return app
