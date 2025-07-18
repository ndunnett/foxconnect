import traceback

from quart import Blueprint, Quart, current_app, render_template
from werkzeug.exceptions import HTTPException, InternalServerError

bp = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/",
    static_url_path="/main/static",
)


def init_app(app: Quart) -> None:
    app.register_blueprint(bp)
    app.config["FOXCONNECT_CONTEXT"]["navbar_links"] |= {
        "main.home": "Home",
    }


@bp.route("/")
async def home() -> str:
    """Home page."""
    return await render_template("home.html.j2", page_name="main.home")


def log_exception(e: Exception) -> None:
    """Output formatted stack trace to app logger as an error."""
    tb = traceback.format_exception(e.__class__, e, e.__traceback__)
    formatted = "\n".join(" " * 2 + s for s in "".join(tb).splitlines())
    current_app.logger.error("\n" + formatted)


async def render_exception(e: HTTPException) -> tuple[str, int | None]:
    """Render template to display exception page."""
    return await render_template("error.html.j2", error=e), e.code


@bp.app_errorhandler(HTTPException)  # type: ignore[arg-type]
async def http_exception_handler(e: HTTPException) -> tuple[str, int | None]:
    """Apply exception handler to app for HTTP errors."""
    log_exception(e)
    return await render_exception(e)


@bp.app_errorhandler(Exception)  # type: ignore[arg-type]
async def generic_exception_handler(e: Exception) -> tuple[str, int | None]:
    """Apply exception handler to app for server errors."""
    log_exception(e)
    return await render_exception(InternalServerError(original_exception=e))
