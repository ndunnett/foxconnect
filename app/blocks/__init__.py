from quart import Blueprint, render_template, request, current_app, make_response
from app.blocks.graphing import create_dot


bp = Blueprint("blocks", __name__, template_folder="templates", static_folder="static", url_prefix="/blocks")

navbar = {}


@bp.route("/<compound>/<block>/detail")
async def view_detail(compound: str, block: str):
    """View block detail"""
    obj = current_app.data.get_block(compound, block)
    return await render_template("view_detail.html.j2", compound=obj.compound, block=obj.name, obj=obj)


@bp.route("/<compound>/<block>/diagram")
async def view_diagram(compound: str, block: str):
    """View diagram using d3-graphviz to render .svg in WebAssembly"""
    obj = current_app.data.get_block(compound, block)
    depth = max(0, min(5, request.args.get("depth", default=1, type=int)))
    return await render_template("view_diagram.html.j2", obj=obj, depth=depth)


@bp.route("/<compound>/<block>/dot")
async def dot(compound: str, block: str):
    """Construct diagram in DOT format and serve as plain text"""
    obj = current_app.data.get_block(compound, block)
    depth = max(0, min(5, request.args.get("depth", default=1, type=int)))
    response = await make_response(await create_dot(obj, depth), 200)
    response.mimetype = "text/plain"
    return response
