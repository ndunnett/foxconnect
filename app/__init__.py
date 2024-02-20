from quart import Quart
from app.data import initialise_data


blueprints = [
    "main",
    "blocks",
    "search",
    "d3-graphviz",
]


def create_app():
    app = Quart(__name__)
    app.data = initialise_data()
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
