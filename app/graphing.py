import pydot
from app.models import *


def create_graph(root: Block, depth: int) -> tuple[set[Block], set[Connection]]:
    """Use breadth first search to graph out related Block and Connection objects to a specified depth"""
    queue = {root}
    blocks = set()
    connections = set()

    for _ in range(depth):
        seen = set()

        for block in queue:
            connections |= block.connections
            seen |= set(c.sink_block if c.source_block == block else c.source_block for c in block.connections)

        blocks |= seen
        queue = seen

    return (blocks, connections)


def create_dot(root: Block, depth: int) -> str:
    """Create a diagram in DOT format using PyDot based on a graph of Block objects"""
    (blocks, connections) = create_graph(root, depth)
    diagram = pydot.Dot("pydot", graph_type="graph", rankdir="LR", ranksep=3)

    # Render root node separately
    diagram.add_node(create_node(root, origin=True))
    blocks.discard(root)

    nodes = [create_node(block) for block in blocks]
    edge = [create_edge(connection) for connection in connections]

    for node in nodes:
        diagram.add_node(node)

    for edge in edge:
        diagram.add_edge(edge)

    return diagram.to_string()


def create_node(block: Block, origin: bool = False) -> pydot.Node:
    """Take Block object and return a PyDot node"""
    # Visual parameters
    con_width = 60
    mid_width = 60
    origin_colour = "#ffd84d"
    other_colour = "#cccccc"

    # Shorthand
    total_width = con_width * 2 + mid_width
    title = str(block)
    blank_cell = f'<td bgcolor="#ffffff00" width="{con_width}" fixedsize="true" href="" title="{title}"></td>'
    mid_cell = f'<td bgcolor="#ffffff00" width="{mid_width}" fixedsize="true" href="" title="{title}"></td>'

    def parameter_cells(parameters: list[str]) -> list[str]:
        """Returns list of HTML table cells for given parameters"""
        return [f'<td bgcolor="#ffffff" border="1" width="{con_width}" fixedsize="true" href="" title="{title}.{p}" port="{p}"><font point-size="9">.{p}</font></td>' for p in parameters]

    # Generate all table cells
    sourced_parameters = sorted(set(c.source_parameter for c in block.connections if c.source_block == block))
    sinked_parameters = sorted(set(c.sink_parameter for c in block.connections if c.sink_block == block))
    outgoing_cells = parameter_cells(sourced_parameters)
    incoming_cells = parameter_cells(sinked_parameters)

    # Generate all table rows
    height = max(len(incoming_cells), len(outgoing_cells))
    title_row = f'<tr><td cellpadding="0" colspan="3" href="" title="{title}"><font point-size="12"><b>{title}</b></font></td></tr>'
    desc_row = f'<tr><td cellpadding="0" colspan="3" href="" title="{title}"><font point-size="10">{block.descrp}</font></td></tr>' if "descrp" in block else ""
    type_row = f'<tr><td cellpadding="0" colspan="3" href="" title="{title}"><font point-size="8"><i>TYPE = {block.type}</i></font></td></tr>'
    parameter_rows = [f"""
    <tr>
        {blank_cell if i >= len(incoming_cells) else incoming_cells[i]}
        {mid_cell}
        {blank_cell if i >= len(outgoing_cells) else outgoing_cells[i]}
    </tr>""" for i in range(height)]

    # Build table
    label = f"""<<table border="0" cellpadding="2" cellspacing="6" width="{total_width}" fixedsize="true">
        {title_row}
        {desc_row if block.descrp else ""}
        {type_row}
        {''.join(parameter_rows)}
    </table>>"""

    # Create node
    fillcolor = origin_colour if origin else other_colour
    tooltip = f'"{title}"'
    return pydot.Node(block.id, tooltip=tooltip, label=label, shape="plain", fontname="sans-serif", style="filled", fillcolor=fillcolor)


def create_edge(connection: Connection) -> pydot.Edge:
    """Take Connection object and return a PyDot edge"""
    source = f'{connection.source_block.id}:{connection.source_parameter}'
    sink = f'{connection.sink_block.id}:{connection.sink_parameter}'
    tooltip = f'"{connection.source_block}.{connection.source_parameter} --> {connection.sink_block}.{connection.sink_parameter}"'
    return pydot.Edge(source, sink, dir="forward", tooltip=tooltip)
