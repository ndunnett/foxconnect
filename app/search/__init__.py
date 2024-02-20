from quart import Blueprint, render_template, request, url_for, jsonify, current_app
from app.data import define_parameters
from app.models import *


bp = Blueprint("search", __name__, template_folder="templates", static_folder="static", url_prefix="/search")

navbar = {
    "search.index": "Search",
}


@bp.route("")
async def index():
    """Search blocks with regex filters (see static/search.js)"""
    columns = {k: v for k, v in request.args.items() if k not in ["page", "lines"]}
    filters = {k: v for k, v in columns.items() if v}
    page = request.args.get("page", default=1, type=int)
    lines = request.args.get("lines", default=19, type=int)
    return await render_template("index.html.j2", page_name="search.index", page=page, lines=lines, columns=columns.keys(), filters=filters)


@bp.route("/query", methods=["POST"])
async def query():
    """Serve structure object as JSON"""
    query = await request.get_json()
    result = list(map(lambda b: {k: getattr(b, k) for k in query.keys()}, current_app.data.query_blocks(query)))

    for r in result:
        r["diagram_url"] = url_for("blocks.view_diagram", compound=r["compound"], block=r["name"])
        r["detail_url"] = url_for("blocks.view_detail", compound=r["compound"], block=r["name"])

    return jsonify(result)


@bp.route("/parameters", methods=["GET"])
async def parameters():
    """Serve parameter data as JSON"""
    return jsonify({p.name: p.dict() for p in define_parameters()})
