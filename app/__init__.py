from flask import Flask
from app.data import initialise_data


def create_app():
    app = Flask(__name__)
    app.data = initialise_data()
    context = {"navbar_links": {}}

    for blueprint in ["main", "blocks", "api", "d3-graphviz"]:
        pkg = __import__(f"app.{blueprint}", globals(), locals(), ["bp", "navbar"], 0)
        app.register_blueprint(pkg.bp)

        try:
            context["navbar_links"] |= pkg.navbar
        except AttributeError:
            pass

    @app.context_processor
    def app_context():
        return context

    return app
