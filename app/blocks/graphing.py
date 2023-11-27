from flask import render_template
from app.models import *


def create_graph(root: Block, depth: int) -> tuple[set[Block], set[Connection]]:
    """Use breadth first search to graph out related Block and Connection objects to a specified depth"""
    queue = {root}
    blocks = {root}
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
    """Create a diagram in DOT format based on a graph of Block objects"""
    origin_colour = "#ffd84d"
    other_colour = "#d4cfca"
    appearance = {
        "con_width": 60,
        "mid_width": 60,
        "parameter_colour": "#ffffff",
        "title_size": 13,
        "descrp_size": 11,
        "type_size": 9,
        "parameter_size": 10,
        "cell_padding": 2,
        "cell_spacing": 6,
    }

    (blocks, connections) = create_graph(root, depth)
    diagram = DotGraph(f"{root.compound}__{root.name}__depth-{depth}", rankdir="LR", ranksep=3, bgcolor="transparent")

    for block in blocks:
        sourced_p = sorted(set(c.source_parameter for c in block.connections if c.source_block == block))
        sinked_p = sorted(set(c.sink_parameter for c in block.connections if c.sink_block == block))
        fillcolor = origin_colour if block == root else other_colour
        label = render_template("graph_node_label.html", len=len, max=max, block=block, sourced_p=sourced_p, sinked_p=sinked_p, appearance=appearance)
        diagram.add_node(block.id, tooltip=str(block), label=label, fontname="Arial", shape="plain", style="filled", fillcolor=fillcolor)

    for connection in connections:
        source = f"{connection.source_block.id}:{connection.source_parameter}"
        sink = f"{connection.sink_block.id}:{connection.sink_parameter}"
        tooltip = f"{connection.source_block}.{connection.source_parameter} --> {connection.sink_block}.{connection.sink_parameter}"
        diagram.add_edge(source, sink, dir="forward", tooltip=tooltip)

    return diagram.to_string()


def quote_if_necessary(p: any) -> str:
    """If p is not wrapped in ', ", or <<>>, escape all double quote and new line characters and wrap p in double quotes"""
    def is_wrapped(p: any, s: str, e=None) -> bool:
        return p.startswith(s) and p.endswith(s) if not e else p.startswith(s) and p.endswith(e)

    if isinstance(p, str):
        if is_wrapped(p, "<<", ">>") or is_wrapped(p, '"') or is_wrapped(p, "'"):
            return p

        else:
            replace = {
                '"': r"\"",
                "\n": r"\n",
                "\r": r"\r",
            }

            for (a, b) in replace.items():
                p = p.replace(a, b)

    return f'"{p}"'


class DotChild:
    """Represents a child of a DOT graph, ie. node/edge"""
    def __init__(self, name: str, **attrs):
        self.name = name
        self.attributes = dict(attrs)

    def to_string(self) -> str:
        output = str(self.name)

        if self.attributes:
            output += "[" + ", ".join([f"{k}={quote_if_necessary(v)}" for k, v in self.attributes.items()]) + "]"

        return output + ";"


class DotGraph:
    """Represents a DOT graph and children"""
    def __init__(self, name="diagram", graph_type="graph", strict=False, **attrs):
        self.name = name
        self.graph_type = graph_type
        self.strict = strict
        self.attributes = dict(attrs)
        self.nodes = []
        self.edges = []

    def add_node(self, name: str, **attrs) -> ():
        self.nodes.append(DotChild(name, **attrs))

    def add_edge(self, src: str, dst: str, **attrs) -> ():
        self.edges.append(DotChild(f"{src} -- {dst}", **attrs))

    def to_string(self) -> str:
        output = [f'{"strict " if self.strict else ""}{self.graph_type} "{self.name}" ' + "{"]

        for k, v in sorted(self.attributes.items()):
            output.append(f"    {k}={quote_if_necessary(v)};")

        output.append("")

        for node in self.nodes:
            output.append(f"    {node.to_string().replace("\n", "\n    ")}\n")

        for edge in self.edges:
            output.append(f"    {edge.to_string()}")

        output.append("}\n")
        return "\n".join(output)
