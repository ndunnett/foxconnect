from quart import Blueprint

"""
Blueprint is here simply to serve node modules for d3-graphviz as static
files. Packages are installed using yarn and symlinks made during project
build, see install_d3graphviz() in app/setup.py for detail.

Use static files in templates like so:

<script src="{{ url_for('d3-graphviz.static', filename='d3.js') }}"></script>
<script src="{{ url_for('d3-graphviz.static', filename='graphviz.umd.js') }}" type="javascript/worker"></script>
<script src="{{ url_for('d3-graphviz.static', filename='d3-graphviz.js') }}"></script>
"""

bp = Blueprint("d3-graphviz", __name__, static_folder="static", url_prefix="/d3-graphviz")
