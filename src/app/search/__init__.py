import math
from functools import cache, reduce
from typing import Optional

from quart import Blueprint, Quart, current_app, render_template, session
from werkzeug.exceptions import BadRequest

from app.search.components import PaginationButton, SearchInput
from quart_foxdata import define_parameters
from quart_htmx import request

bp = Blueprint("search", __name__, template_folder="templates", static_folder="static", url_prefix="/search")


def init_app(app: Quart) -> None:
    app.register_blueprint(bp)
    app.config["FOXCONNECT_CONTEXT"]["navbar_links"] |= {
        "search.index": "Search",
    }


def generate_pagination(page: int, lines: int, total: int) -> list[PaginationButton]:
    last_page = math.ceil(total / lines)
    indices = filter(lambda x: 0 < x <= last_page, (1, page - 2, page - 1, page, page + 1, page + 2, last_page))

    def fold_indices(acc: list[PaginationButton], i: int) -> list[PaginationButton]:
        if len(acc) == 0 or (len(acc) > 0 and i > acc[-1].value):
            if len(acc) > 0 and i - acc[-1].value > 1:
                acc.append(PaginationButton(disabled=True))
            acc.append(PaginationButton(value=i, active=i == page))
        return acc

    prev = PaginationButton(label="←", value=page - 1, disabled=page == 1)
    next = PaginationButton(label="→", value=page + 1, disabled=page == last_page)
    return [prev] + reduce(fold_indices, indices, list()) + [next]


@cache
def get_parameter_title(parameter_id: str) -> Optional[str]:
    if parameter := define_parameters().get(parameter_id.upper()):
        return parameter.title
    else:
        return None


def generate_search_inputs(fields: tuple[str, Optional[str]]) -> dict[str, SearchInput]:
    return {key: SearchInput(key, label=get_parameter_title(key), value=value) for key, value in fields}


def fetch_data(query):
    data = current_app.data.query_blocks(query["fields"])
    start = (query["page"] - 1) * query["lines"]
    end = start + query["lines"]
    total = len(data)

    return {
        "fields": dict(query["fields"]),
        "results": data[start:end],
        "page_number": query["page"],
        "total_results": total,
        "pagination": generate_pagination(query["page"], query["lines"], total),
    }


def default_fields() -> tuple:
    return (
        ("compound", ""),
        ("name", ""),
        ("type", ""),
        ("cp", ""),
    )


@bp.route("")
async def index():
    query = {
        "page": session.get("page", 1),
        "lines": session.get("lines", 18),
        "fields": session.get("fields", default_fields()),
    }

    return await render_template(
        "search_index.html.j2",
        page_name="search.index",
        search_inputs=generate_search_inputs(query["fields"]),
        **fetch_data(query),
    )


@bp.route("/table_body", methods=["POST"])
async def table_body():
    if request.hx_request:
        form = await request.form
        fields = {key.split("query-")[-1]: val for key, val in form.items() if key.startswith("query-")}

        query = {
            "page": form.get("page", default=1, type=int),
            "lines": form.get("lines", default=18, type=int),
            "fields": tuple(fields.items()),
        }

        session["page"] = query["page"]
        session["lines"] = query["lines"]
        session["fields"] = query["fields"]

        return await render_template("search_table_body.html.j2", **fetch_data(query))

    raise BadRequest()
