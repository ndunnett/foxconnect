from flask import Blueprint, render_template, request, current_app


bp = Blueprint("blocks", __name__, template_folder="templates", static_folder="static", url_prefix="/blocks")

navbar = {}


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
