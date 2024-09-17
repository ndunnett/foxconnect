from importlib import import_module

from quart import Quart

from quart_d3graphviz import D3Graphviz
from quart_foxdata import FoxData


def create_app():
    app = Quart(__name__)
    app.config["FOXCONNECT_CONTEXT"] = {"navbar_links": {}}
    app.config.from_prefixed_env()

    # initialise extensions
    for extension_class in (D3Graphviz, FoxData):
        extension_class().init_app(app)

    # initialise blueprints
    for module_name in ("main", "blocks", "search"):
        import_module(f"app.{module_name}").init_app(app)

    # add custom context processor
    @app.context_processor
    def foxconnect_context():
        return app.config["FOXCONNECT_CONTEXT"]

    return app
