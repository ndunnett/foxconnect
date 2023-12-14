from flask import Blueprint, render_template, request, current_app
from pprint import pprint


bp = Blueprint("blocks", __name__, template_folder="templates", static_folder="static", url_prefix="/blocks")

navbar = {
    "blocks.search": "Search",
}


@bp.route("/search")
def search():
    """Search blocks with regex filters (see static/search.js)"""
    columns = {k: v for k, v in request.args.items() if k not in ["page", "lines"]}
    filters = {k: v for k, v in columns.items() if v}
    page = request.args.get("page", default=1, type=int)
    lines = request.args.get("lines", default=19, type=int)
    return render_template("search/index.html", page_name="blocks.search", page=page, lines=lines, columns=columns.keys(), filters=filters)


@bp.route("/<compound>/<block>/detail")
def view_detail(compound: str, block: str):
    """View block detail"""
    obj = current_app.data.get_block(compound, block)
    return render_template("view_detail.html", compound=obj.compound, block=obj.name, obj=obj)


@bp.route("/<compound>/<block>/diagram")
def view_diagram(compound: str, block: str):
    """View diagram using d3-graphviz to render .svg in WebAssembly"""
    obj = current_app.data.get_block(compound, block)
    depth = max(0, min(5, request.args.get("depth", default=1, type=int)))
    return render_template("view_diagram.html", obj=obj, depth=depth)
