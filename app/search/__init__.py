from quart import Blueprint, render_template, request, Request, jsonify, current_app
from app.data import define_parameters
from app.models import *
from pprint import pprint


bp = Blueprint("search", __name__, template_folder="templates", static_folder="static", url_prefix="/search")

navbar = {
    "search.index": "Search",
}

LOCAL_DATA_DEFAULT = {
    "page": 1,
    "lines": 20,
    "query": [
        ["compound", ""],
        ["name", ""],
        ["type", ""],
        ["cp", ""],
    ],
}


async def get_local_data(request: Request):
    """Retrieves local data from request body"""
    local_data = LOCAL_DATA_DEFAULT | await request.get_json()

    if "query" in local_data:
        local_data["query"] = dict(local_data["query"])

    return local_data


@bp.route("/table_head", methods=["POST"])
async def table_head():
    """Serve table head based on metadata as html"""
    ld = await get_local_data(request)
    return await render_template("table_head.html.j2", ld=ld, parameters=define_parameters())


@bp.route("/table_body", methods=["POST"])
async def table_body():
    """Serve table body based on metadata as html"""
    ld = await get_local_data(request)
    query_data = current_app.data.query_blocks(tuple(ld["query"].items()))
    start = (ld["page"] - 1) * ld["lines"]
    end = start + ld["lines"]
    return await render_template("table_body.html.j2", ld=ld, data_page=query_data[start:end])


@bp.route("/table_metadata", methods=["POST"])
async def table_metadata():
    """Serve metadata for table as json"""
    metadata = await get_local_data(request)
    metadata["query"] = tuple(metadata["query"].items())
    metadata["total"] = len(current_app.data.query_blocks(metadata["query"]))
    return jsonify(metadata)


@bp.route("")
async def index():
    """Index page for searching blocks with regex filters"""
    return await render_template("index.html.j2", page_name="search.index")
