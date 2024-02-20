from quart import Blueprint, render_template


bp = Blueprint("main", __name__, template_folder="templates", static_folder="static", url_prefix="/", static_url_path="/main/static")

navbar = {
    "main.home": "Home",
}


@bp.route("/")
async def home():
    """Home page"""
    return await render_template("home.html.j2", page_name="main.home")
