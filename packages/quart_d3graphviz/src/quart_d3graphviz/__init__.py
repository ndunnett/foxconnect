import importlib.resources
from typing import Optional

from quart import Blueprint, Quart


class D3Graphviz:
    def __init__(self, app: Optional[Quart] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        app.extensions["d3graphviz"] = self
        node_modules = importlib.resources.files("quart_d3graphviz") / "node_modules"
        blueprint = Blueprint("d3graphviz", __name__, static_folder=node_modules, url_prefix="/d3graphviz")
        app.register_blueprint(blueprint)
