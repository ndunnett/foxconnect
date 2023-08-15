import re
from io import BytesIO
from flask import Flask, render_template, send_file, request, url_for, redirect, jsonify
from backend.graphing import create_diagram
from backend.utilities import is_number, to_number
from backend.data import initialise_data
from functools import cache


# Data object to contain block and connection objects
data = initialise_data()
app = Flask(__name__)


@app.context_processor
def context():
    """Add functions and variables to template context"""
    return dict(enumerate=enumerate, data=data)


def serve_svg(content: bytes):
    """Takes bytes and serves as SVG XML"""
    svg_io = BytesIO()
    svg_io.write(content)
    svg_io.seek(0)
    return send_file(svg_io, mimetype="image/svg+xml")


@app.route("/data/structure.json")
def get_structure_json():
    """Serve structure object as JSON"""
    return jsonify(data.get_structure())


@app.route("/data/<compound>/<block>/depth-<depth>/diagram.svg", methods=("GET", "HEAD"))
def make_diagram(compound: str, block: str, depth: str):
    """Make diagram and render to SVG using GraphViz and PyDot"""
    return serve_svg(create_diagram(data.find_block(compound, block), to_number(depth)))


@app.route("/<compound>/<block>/diagram/")
def view_diagram(compound: str, block: str):
    """View diagram using leaflet"""
    compound = compound.upper()
    block = block.upper()
    depth = max(0, min(5, request.args.get("depth", default=1, type=int)))
    diagram_url = url_for("make_diagram", compound=compound, block=block, depth=depth)
    return render_template("view_diagram.html", compound=compound, block=block, depth=depth, diagram_url=diagram_url)


@app.route("/<compound>/<block>/detail/")
def view_detail(compound: str, block: str):
    """View block detail"""
    compound = compound.upper()
    block = block.upper()
    block_object = data.find_block(compound, block)
    return render_template("view_detail.html", compound=compound, block=block, block_object=block_object)


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


@app.route("/")
def search():
    """Search page to find available compounds/blocks"""

    return render_template("search.html", title="FoxConnect")


@app.route("/index/")
def index():
    """Index showing available compounds/blocks"""

    @cache
    def get_compounds():
        compound_names = data.compounds.keys()
        blowers = re.findall(r"([\d]_[\d]_COMPR)", "\n".join(compound_names))
        units = [str(i) for i in range(1, 7)]
        compounds = {f"Unit {unit}": [compound for compound in compound_names if compound.startswith(unit) and compound not in blowers] for unit in units}
        compounds["Station"] = blowers + [compound for compound in compound_names if not compound.startswith((*units,))]
        return compounds

    return render_template("index.html", title="FoxConnect", compounds=get_compounds())
