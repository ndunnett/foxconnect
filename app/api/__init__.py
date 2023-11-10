from flask import Blueprint, request, url_for, jsonify, current_app
from app.graphing import create_diagram
from app.utilities import serve_svg, to_number
from app.data import define_parameters


bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/query", methods=["POST"])
def query():
    """Serve structure object as JSON"""
    query = request.get_json()
    result = list(map(lambda b: {k: getattr(b, k) for k in query.keys()}, current_app.data.query_blocks(query)))

    for r in result:
        r["diagram_url"] = url_for("blocks.view_diagram", compound=r["compound"], block=r["name"])
        r["detail_url"] = url_for("blocks.view_detail", compound=r["compound"], block=r["name"])

    return jsonify(result)


@bp.route("/parameters", methods=["GET"])
def parameters():
    """Serve parameter data as JSON"""
    return jsonify({p.name: p.dict() for p in define_parameters()})


@bp.route("/diagram/<compound>__<block>__depth-<depth>.svg", methods=("GET", "HEAD"))
def make_diagram(compound: str, block: str, depth: str):
    """Make diagram and render to SVG using GraphViz and PyDot"""
    return serve_svg(create_diagram(current_app.data.get_block(compound, block), to_number(depth)))
