from io import BytesIO
from flask import Flask, render_template, send_file, request, url_for, redirect, jsonify
from .graphing import create_diagram
from .utilities import is_number, to_number
from .data import initialise_data, define_parameters


# Data object to contain block and connection objects
data = initialise_data()

# App context
app = Flask(__name__)

# Links to put in header navbar (<method name>: <title>)
navbar_links = {
    "home": "Home",
    "search": "Search",
}


@app.context_processor
def context():
    """Add functions and variables to template context"""
    return dict(
        enumerate=enumerate,
        data=data,
        navbar_links=navbar_links
    )


@app.route("/api/query", methods=["POST"])
def query():
    """Serve structure object as JSON"""
    query = request.get_json()
    result = list(map(lambda b: {k: getattr(b, k) for k in query.keys()}, data.query_blocks(query)))

    for r in result:
        r["diagram_url"] = url_for("view_diagram", compound=r["compound"], block=r["name"])
        r["detail_url"] = url_for("view_detail", compound=r["compound"], block=r["name"])

    return jsonify(result)


@app.route("/api/parameters", methods=["GET"])
def parameters():
    """Serve parameter data as JSON"""
    return jsonify({p.name: p.dict() for p in define_parameters()})


@app.route("/")
def home():
    """Home page"""
    return render_template("layout/base.html", page_name="home")


@app.route("/search")
def search():
    """Search blocks with regex filters (see static/script/search.js)"""
    return render_template("pages/search.html", page_name="search")


def serve_svg(content: bytes):
    """Takes bytes and serves as SVG XML"""
    svg_io = BytesIO()
    svg_io.write(content)
    svg_io.seek(0)
    return send_file(svg_io, mimetype="image/svg+xml")


@app.route("/data/<compound>/<block>/depth-<depth>/diagram.svg", methods=("GET", "HEAD"))
def make_diagram(compound: str, block: str, depth: str):
    """Make diagram and render to SVG using GraphViz and PyDot"""
    return serve_svg(create_diagram(data.get_block(compound, block), to_number(depth)))


@app.route("/<compound>/<block>/diagram")
def view_diagram(compound: str, block: str):
    """View diagram using leaflet"""
    compound = compound.upper()
    block = block.upper()
    depth = max(0, min(5, request.args.get("depth", default=1, type=int)))
    diagram_url = url_for("make_diagram", compound=compound, block=block, depth=depth)
    return render_template("model_views/view_diagram.html", compound=compound, block=block, depth=depth, diagram_url=diagram_url)


@app.route("/<compound>/<block>/detail")
def view_detail(compound: str, block: str):
    """View block detail"""
    obj = data.get_block(compound, block)
    return render_template("model_views/view_detail.html", compound=obj.compound, block=obj.name, obj=obj)


@app.route("/go_to_diagram", methods=["POST"])
def go_to_diagram():
    """Redirect to the diagram specified by form parameters"""
    compound = request.form["compound-input"].upper()
    block = request.form["block-input"].upper()
    depth = request.form["depth-select"]
    depth_ext = "" if not is_number(depth) or to_number(depth) < 0 else f'?depth={depth}'
    view_url = url_for("view_diagram", compound=compound, block=block) + depth_ext
    return redirect(view_url)


@app.route("/go_to_detail", methods=["POST"])
def go_to_detail():
    """Redirect to the diagram specified by form parameters"""
    compound = request.form["compound-input"].upper()
    block = request.form["block-input"].upper()
    return redirect(url_for("view_detail", compound=compound, block=block))

