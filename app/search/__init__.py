from quart import Blueprint, render_template, request


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
