from quart import Blueprint, render_template, Request, request, current_app
from werkzeug.exceptions import NotFound
from functools import cache
from app.blocks.graphing import create_dot
from app.models import *
from app.utilities import serve_plain_text


bp = Blueprint("blocks", __name__, template_folder="templates", static_folder="static", url_prefix="/blocks")

navbar = {}


@cache
def get_obj(compound: str, block: str) -> Block:
    """Retrieve block object from application state and handle 'not found' error"""
    data: Data = current_app.data
    if (obj := data.get_block(compound, block)):
        return obj
    else:
        if compound in data.compounds:
            raise NotFound(f"Block \"{block}\" not found in compound \"{compound}\".")
        else:
            raise NotFound(f"Compound \"{compound}\" not found.")


def get_depth(request: Request) -> int:
    """Retrieve and validate depth parameter from request args"""
    return max(0, min(5, request.args.get("depth", default=1, type=int)))


@bp.route("/<compound>/<block>/detail")
async def view_detail(compound: str, block: str):
    """View block detail"""
    return await render_template("view_detail.html.j2", obj=get_obj(compound, block))


@bp.route("/<compound>/<block>/diagram")
async def view_diagram(compound: str, block: str):
    """View diagram using d3-graphviz to render .svg in WebAssembly"""
    return await render_template("view_diagram.html.j2", obj=get_obj(compound, block), depth=get_depth(request))


@bp.route("/<compound>/<block>/dot")
async def dot(compound: str, block: str):
    """Construct diagram in DOT format and serve as plain text"""
    return await serve_plain_text(await create_dot(get_obj(compound, block), get_depth(request)))
