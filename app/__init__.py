from quart import Quart
from pathlib import Path
from app.data import initialise_data


# Path definitions
ICC_DUMPS_PATH = Path(__file__).resolve().parent.parent.parent / "icc_dumps"
PICKLE_PATH = Path(__file__).resolve().parent / "pickle"
DATA_PICKLE_PATH = PICKLE_PATH / "data.pickle"

# Glob to find CP dump files
DUMP_FILE_GLOB = ICC_DUMPS_PATH.glob("*/*.d")


blueprints = [
    "main",
    "blocks",
    "search",
    "d3-graphviz",
]


def create_app():
    app = Quart(__name__)
    app.data = initialise_data(DATA_PICKLE_PATH, DUMP_FILE_GLOB)
    context = {"navbar_links": {}}

    for blueprint in blueprints:
        pkg = __import__(f"app.{blueprint}", globals(), locals(), ["bp", "navbar"], 0)
        app.register_blueprint(pkg.bp)

        try:
            context["navbar_links"] |= pkg.navbar
        except AttributeError:
            pass

    @app.context_processor
    def _app_context():
        return context

    return app
