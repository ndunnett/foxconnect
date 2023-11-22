from flask import Blueprint, request, url_for, jsonify, current_app, make_response
from app.graphing import create_dot
from app.utilities import to_number
from app.data import define_parameters
from app.models import *


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


@bp.route("/dot/<compound>__<block>__depth-<depth>")
def dot(compound: str, block: str, depth: str):
    """Use PyDot to construct diagram in DOT format and serve as plain text"""
    obj = current_app.data.get_block(compound, block)
    depth = max(0, min(5, to_number(depth)))
    response = make_response(create_dot(obj, depth), 200)
    response.mimetype = "text/plain"
    return response
