from quart import Blueprint


bp = Blueprint("d3-graphviz", __name__, static_folder="static", url_prefix="/d3-graphviz")

# Blueprint is here simply to install/build node packages for d3-graphviz and serve them as static files
#
# Use static files in templates like so:
#
# <script src="{{ url_for('d3-graphviz.static', filename='d3.js') }}"></script>
# <script src="{{ url_for('d3-graphviz.static', filename='graphviz.umd.js') }}" type="javascript/worker"></script>
# <script src="{{ url_for('d3-graphviz.static', filename='d3-graphviz.js') }}"></script>
