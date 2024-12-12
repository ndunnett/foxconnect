import datetime
import math
from functools import reduce
from io import BytesIO

from quart import Blueprint, Quart, Response, current_app, render_template, send_file, session
from quart_htmx import BadHtmxRequest, request
from xlsxwriter import Workbook

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

    prev_button = PaginationButton(label="←", value=page - 1, disabled=page <= 1)
    next_button = PaginationButton(label="→", value=page + 1, disabled=page >= last_page)
    return [prev_button, *reduce(fold_indices, indices, []), next_button]


def generate_search_inputs(fields: tuple[tuple[str, str | None], ...]) -> dict[str, SearchInput]:
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
async def index() -> str:
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
async def table() -> str:
    """Render the table body dynamic content via HTMX."""

    if request.hx_request:
        form = await request.form
        parameters = [key.removeprefix("parameter-").upper() for key in form if key.startswith("parameter-")]

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
async def configuration() -> str:
    """Render the configuration panel via HTMX."""

    if request.hx_request:
        current_params = [
            RemovableParameter(name, pinned=(name.upper() in ("COMPOUND", "NAME")))
            for name, _ in session.get("fields", DEFAULT_FIELDS)
        ]

        return await render_template("search_configuration.html.j2", current_params=current_params)

    raise BadHtmxRequest()


@bp.route("/delete", methods=["DELETE"])
async def delete() -> str:
    """Return an empty string for HTMX delete requests."""

    return ""


@bp.route("/add_parameter", methods=["GET"])
async def add_parameter() -> str:
    """Get a parameter to add to the queried parameters in the configuration panel."""

    if request.hx_request and (trigger := request.hx_trigger) and (name := trigger.removeprefix("add-").upper()):
        return str(RemovableParameter(name))

    raise BadHtmxRequest()


@bp.route("/search_parameters", methods=["POST"])
async def search_parameters() -> str:
    """Get a list of parameters that can be added in the configuration panel."""

    if request.hx_request:
        form = await request.form

        if query := form.get("search-parameters"):
            if parameters := current_app.data.query_parameters(query):  # type: ignore
                return "\n".join(str(AddableParameter(p.source)) for p in parameters)
            else:
                return str(AddableParameter(query.strip(".").upper()))
        else:
            return ""

    raise BadHtmxRequest()


def auto_type(s: str) -> str | float:
    """Convert string to float if it is a number."""
    try:
        return float(s)
    except ValueError:
        return s


@bp.route("/export_spreadsheet", methods=["GET"])
async def export_spreadsheet() -> Response:
    """Generate spreadsheet and serve file to download."""

    fields = session["fields"]
    data = current_app.data.query_blocks(fields)  # type: ignore
    file = BytesIO()

    options = {
        "columns": [{"header": field} for field, _ in fields],
        "data": [[auto_type(val) for val in result.values()] for result in data],
        "style": "Table Style Light 1",
    }

    with Workbook(file) as workbook:
        worksheet = workbook.add_worksheet()
        worksheet.add_table(0, 0, len(data), len(fields) - 1, options)
        worksheet.autofit()

    timestamp = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=10)))

    return await send_file(
        file,
        as_attachment=True,
        attachment_filename=f"{timestamp:%Y-%m-%d_%H%M}_foxconnect_search.xlsx",
    )
