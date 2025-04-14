from quart import Quart

from .d3graphviz import D3Graphviz
from .foxdata import FoxData
from .htmx import Htmx


def init_app(app: Quart) -> None:
    FoxData().init_app(app)
    D3Graphviz().init_app(app)
    Htmx().init_app(app)
