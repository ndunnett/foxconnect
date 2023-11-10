from flask import Blueprint, render_template, request, url_for, current_app


bp = Blueprint("blocks", __name__, template_folder="templates", static_folder="static", url_prefix="/block")

navbar = {
    "blocks.search": "Search",
}


@bp.route("/search")
def search():
    """Search blocks with regex filters (see static/search.js)"""
    return render_template("search.html", page_name="blocks.search")


@bp.route("/<compound>/<block>/detail")
def view_detail(compound: str, block: str):
    """View block detail"""
    obj = current_app.data.get_block(compound, block)
    return render_template("view_detail.html", compound=obj.compound, block=obj.name, obj=obj)


@bp.route("/<compound>/<block>/diagram")
def view_diagram(compound: str, block: str):
    """View diagram using leaflet"""
    compound = compound.upper()
    block = block.upper()
    depth = max(0, min(5, request.args.get("depth", default=1, type=int)))
    diagram_url = url_for("api.make_diagram", compound=compound, block=block, depth=depth)
    return render_template("view_diagram.html", compound=compound, block=block, depth=depth, diagram_url=diagram_url)
