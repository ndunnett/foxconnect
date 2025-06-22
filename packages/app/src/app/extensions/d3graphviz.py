from pyd3graphviz import d3graphviz_node_modules
from quart import Blueprint, Quart


class D3Graphviz:
    """
    Quart extension to serve d3-graphviz for client side graph rendering.

    Distribution files from the d3-graphviz Node package are served as static files
    via a blueprint called "d3graphviz".
    """

    def __init__(self, app: Quart | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        """
        Initialise the extension for a given Quart instance.

        * Registers the extension with the app
        * Creates the blueprint to serve static files
        """
        blueprint = Blueprint("d3graphviz", __name__, static_folder=d3graphviz_node_modules(), url_prefix="/d3graphviz")
        app.register_blueprint(blueprint)
        app.extensions["d3graphviz"] = self
