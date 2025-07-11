from quart import Quart

from . import blocks, calc, main, search


def init_app(app: Quart) -> None:
    main.init_app(app)
    blocks.init_app(app)
    search.init_app(app)
    calc.init_app(app)
