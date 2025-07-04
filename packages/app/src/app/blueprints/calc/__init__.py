from foxdata.models import Block
from foxemu.blocks.calc import Calc
from quart import Blueprint, Quart, make_response, render_template
from werkzeug.exceptions import NotFound

from app.extensions.foxdata import get_block_from_name
from app.extensions.htmx import Response

bp = Blueprint("calc", __name__, template_folder="templates", static_folder="static", url_prefix="/calc")


def init_app(app: Quart) -> None:
    app.register_blueprint(bp)


def get_obj(compound: str, block: str) -> Block:
    """Retrieve block object from application state."""
    if obj := get_block_from_name(compound, block):
        return obj
    else:
        description = f'Block "{compound}:{block}" not found.'
        raise NotFound(description)


async def serve_plain_text(content: str) -> Response:
    """Serve content as plain text."""
    response = await make_response(content, 200)
    response.mimetype = "text/plain"
    return response  # type: ignore[return-value]


@bp.route("/<compound>/<block>/diagram")
async def view_diagram(compound: str, block: str) -> str:
    """."""
    return await render_template("view_logic_flow.html.j2", obj=get_obj(compound, block))


@bp.route("/<compound>/<block>/dot")
async def dot(compound: str, block: str) -> Response:
    """Construct diagram in DOT format and serve as plain text."""
    calc = Calc.from_block(get_obj(compound, block))
    return await serve_plain_text(calc.generate_dot())
