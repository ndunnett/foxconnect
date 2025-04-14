from quart import Quart

from . import blocks, main, search


def init_app(app: Quart) -> None:
    main.init_app(app)
    blocks.init_app(app)
    search.init_app(app)
