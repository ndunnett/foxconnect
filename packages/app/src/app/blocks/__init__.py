from quart import Blueprint, Quart, Request, current_app, make_response, render_template, request
from quart_foxdata.models import Block
from quart_htmx import Response
from werkzeug.exceptions import NotFound

from app.blocks.graphing import create_dot

bp = Blueprint("blocks", __name__, template_folder="templates", static_folder="static", url_prefix="/blocks")


def init_app(app: Quart) -> None:
    app.register_blueprint(bp)


def get_obj(compound: str, block: str) -> Block:
    """Retrieve block object from application state."""
    if obj := current_app.data.get_block_from_name(compound, block):  # type: ignore
        return obj
    else:
        raise NotFound(f'Block "{compound}:{block}" not found.')


async def serve_plain_text(content: str) -> Response:
    """Serve content as plain text."""
    response = await make_response(content, 200)
    response.mimetype = "text/plain"
    return response  # type: ignore


def get_depth(request: Request) -> int:
    """Retrieve and validate depth parameter from request args."""
    return max(0, min(5, request.args.get("depth", default=1, type=int)))


@bp.route("/<compound>/<block>/detail")
async def view_detail(compound: str, block: str) -> str:
    """View block detail."""
    return await render_template("view_detail.html.j2", obj=get_obj(compound, block))


@bp.route("/<compound>/<block>/diagram")
async def view_diagram(compound: str, block: str) -> str:
    """View diagram using d3-graphviz to render .svg in WebAssembly."""
    return await render_template("view_diagram.html.j2", obj=get_obj(compound, block), depth=get_depth(request))


@bp.route("/<compound>/<block>/dot")
async def dot(compound: str, block: str) -> Response:
    """Construct diagram in DOT format and serve as plain text."""
    return await serve_plain_text(await create_dot(current_app.data, get_obj(compound, block), get_depth(request)))  # type: ignore
