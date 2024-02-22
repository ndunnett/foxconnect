from quart import Blueprint, render_template
from werkzeug.exceptions import HTTPException, InternalServerError


bp = Blueprint("main", __name__, template_folder="templates", static_folder="static",
               url_prefix="/", static_url_path="/main/static")

navbar = {
    "main.home": "Home",
}


@bp.route("/")
async def home():
    """Home page"""
    return await render_template("home.html.j2", page_name="main.home")


@bp.app_errorhandler(Exception)
async def exception_handler(e):
    """Generic app wide exception handler"""
    if isinstance(e, HTTPException):
        return await render_template("error.html.j2", error=e), e.code
    else:
        return await render_template("error.html.j2", error=InternalServerError), 500
