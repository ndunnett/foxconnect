import math
from functools import reduce
from typing import Optional

from quart import Blueprint, Quart, current_app, render_template, session
from quart_foxdata import query_parameters
from quart_htmx import BadHtmxRequest, request

from app.search.components import AddableParameter, PaginationButton, RemovableParameter, SearchInput

bp = Blueprint("search", __name__, template_folder="templates", static_folder="static", url_prefix="/search")


DEFAULT_FIELDS = (
    ("COMPOUND", ""),
    ("NAME", ""),
    ("TYPE", ""),
    ("CP", ""),
)


def init_app(app: Quart) -> None:
    app.register_blueprint(bp)
    app.config["FOXCONNECT_CONTEXT"]["navbar_links"] |= {
        "search.index": "Search",
    }


def generate_pagination(page: int, lines: int, total: int) -> list[PaginationButton]:
    """Generate pagination components for given page, lines, and total results."""

    last_page = math.ceil(total / lines)
    indices = filter(lambda x: 0 < x <= last_page, (1, page - 2, page - 1, page, page + 1, page + 2, last_page))

    def fold_indices(acc: list[PaginationButton], i: int) -> list[PaginationButton]:
        """Inserts a disabled button between page number gaps and filters out repeated indices."""
        empty = len(acc) == 0
        repeated = not empty and (last := acc[-1].value) is not None and i == last
        discontinuous = not empty and (last := acc[-1].value) is not None and i - last != 1

        if not repeated:
            if discontinuous:
                acc.append(PaginationButton(disabled=True))
            acc.append(PaginationButton(value=i, active=i == page))

        return acc

    prev = PaginationButton(label="←", value=page - 1, disabled=page == 1)
    next = PaginationButton(label="→", value=page + 1, disabled=page == last_page)
    initial: list[PaginationButton] = list()
    return [prev] + reduce(fold_indices, indices, initial) + [next]


def generate_search_inputs(fields: tuple[tuple[str, Optional[str]], ...]) -> dict[str, SearchInput]:
    """Generate search input components for the table header."""
    return {key: SearchInput(key, value=value) for key, value in fields}


def fetch_data(query: dict) -> dict:
    """Process query to fetch all data and components needed to render the table body and footer."""

    data = current_app.data.query_blocks(query["fields"])  # type: ignore
    start = (query["page"] - 1) * query["lines"]
    end = start + query["lines"]
    total = len(data)

    current_params = [
        RemovableParameter(name, pinned=(name.upper() in ("COMPOUND", "NAME")))
        for name, _ in session.get("fields", DEFAULT_FIELDS)
    ]

    return {
        "fields": dict(query["fields"]),
        "results": data[start:end],
        "page_number": query["page"],
        "total_results": total,
        "pagination": generate_pagination(query["page"], query["lines"], total),
        "current_params": current_params,
    }


@bp.route("")
async def index():
    """Render the main search index page."""

    query = {
        "page": session.get("page", 1),
        "lines": session.get("lines", 18),
        "fields": session.get("fields", DEFAULT_FIELDS),
    }

    return await render_template(
        "search_index.html.j2",
        page_name="search.index",
        search_inputs=generate_search_inputs(query["fields"]),
        **fetch_data(query),
    )


@bp.route("/table", methods=["POST"])
async def table():
    """Render the table body dynamic content via HTMX."""

    if request.hx_request:
        form = await request.form
        parameters = [key.removeprefix("parameter-").upper() for key in form.keys() if key.startswith("parameter-")]

        if len(parameters):
            current_fields = {key.removeprefix("query-"): val for key, val in form.items() if key.startswith("query-")}
            fields = {key: current_fields.get(key) or "" for key in parameters}
        else:
            fields = {key.removeprefix("query-"): val for key, val in form.items() if key.startswith("query-")}

        query = {
            "page": form.get("page", default=1, type=int),
            "lines": form.get("lines", default=18, type=int),
            "fields": tuple(fields.items()),
        }

        session["page"] = query["page"]
        session["lines"] = query["lines"]
        session["fields"] = query["fields"]

        return await render_template(
            "search_table.html.j2",
            search_inputs=generate_search_inputs(query["fields"]),
            **fetch_data(query),
        )

    raise BadHtmxRequest()


@bp.route("/configuration", methods=["GET"])
async def configuration():
    """Render the configuration panel via HTMX."""

    if request.hx_request:
        current_params = [
            RemovableParameter(name, pinned=(name.upper() in ("COMPOUND", "NAME")))
            for name, _ in session.get("fields", DEFAULT_FIELDS)
        ]

        return await render_template("search_configuration.html.j2", current_params=current_params)

    raise BadHtmxRequest()


@bp.route("/delete", methods=["DELETE"])
async def delete():
    """Return an empty string for HTMX delete requests."""

    return ""


@bp.route("/add_parameter", methods=["GET"])
async def add_parameter():
    """Get a parameter to add to the queried parameters in the configuration panel."""

    if request.hx_request:
        if name := request.hx_trigger.removeprefix("add-").upper():
            return str(RemovableParameter(name))

    raise BadHtmxRequest()


@bp.route("/search_parameters", methods=["POST"])
async def search_parameters():
    """Get a list of parameters that can be added in the configuration panel."""

    if request.hx_request:
        form = await request.form

        if query := form.get("search-parameters"):
            if parameters := query_parameters(query):
                return "\n".join(str(AddableParameter(p.source)) for p in parameters)
            else:
                return str(AddableParameter(query))
        else:
            return ""

    raise BadHtmxRequest()
