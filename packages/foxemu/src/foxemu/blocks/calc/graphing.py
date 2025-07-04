from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from itertools import pairwise

from pydot import Dot, Edge, Node

from .block import Calc, Step
from .constants import (
    BRANCH_INSTRUCTIONS,
    END_STEP_NUMBER,
    SPECIAL_INSTRUCTIONS,
    TERMINATION_INSTRUCTIONS,
)
from .errors import GraphingError


@dataclass
class Group:
    steps: list[Step]

    def to_node(self, group: int) -> Node:
        node_style = "rounded" if self.steps[0].opcode in ("START", *TERMINATION_INSTRUCTIONS) else ""
        node_label = "\n".join(
            " ".join([step.opcode] + [str(operand) for operand in step.operands]) for step in self.steps
        )
        return Node(
            name=f"Step {group}",
            label=node_label,
            shape="box",
            style=node_style,
            regular="false",
            fontname="Arial",
        )


class Condition(Enum):
    BIF = auto()
    BIZ = auto()
    BII = auto()
    BIN = auto()
    BIP = auto()
    BIT = auto()

    @staticmethod
    def from_str(string: str) -> Condition:
        match string:
            case "BIF":
                return Condition.BIF
            case "BIZ":
                return Condition.BIZ
            case "BII":
                return Condition.BII
            case "BIN":
                return Condition.BIN
            case "BIP":
                return Condition.BIP
            case "BIT":
                return Condition.BIT
            case _:
                msg = "invalid condition opcode"
                raise RuntimeError(msg)

    def to_node(self, group: int) -> Node:
        match self:
            case Condition.BIF | Condition.BIZ:
                node_label = "== 0?"
            case Condition.BII:
                node_label = "block\ninit?"
            case Condition.BIN:
                node_label = "< 0?"
            case Condition.BIP:
                node_label = ">= 0?"
            case Condition.BIT:
                node_label = "!= 0?"

        return Node(
            name=f"Step {group}",
            label=node_label,
            shape="diamond",
            regular="true",
            fixedsize="true",
            height=0.8,
            width=0.8,
            fontname="Arial",
        )


@dataclass
class GraphEdge:
    src: int
    dst: int
    label: str = ""

    def to_edge(self) -> Edge:
        return Edge(
            src=f"Step {self.src}",
            dst=f"Step {self.dst}",
            label=self.label,
            dir="forward",
            fontname="Arial",
        )


class Graph:
    name: str
    nodes: dict[int, Group | Condition]
    edges: list[GraphEdge]

    def __init__(self, block: Calc) -> None:
        self.name = f"{block.compound}__{block.name}__calc"
        self.nodes = {}
        self.edges = []

    def to_dot(self) -> Dot:
        dot = Dot(
            self.name,
            graph_type="graph",
            rankdir="LR",
            bgcolor="transparent",
        )

        for i, node in self.nodes.items():
            dot.add_node(node.to_node(i))

        for edge in self.edges:
            dot.add_edge(edge.to_edge())

        return dot

    @staticmethod
    def from_block(block: Calc) -> Graph | GraphingError:
        """Parse Calc block into a logic flow graph of steps grouped by sequential execution."""
        graph = Graph(block)
        steps = block.steps.copy()

        # Prepopulate start and end steps
        steps[0] = Step(opcode="START", operands=())
        steps[END_STEP_NUMBER] = Step(opcode="END", operands=())
        graph.nodes[END_STEP_NUMBER] = Group([steps[END_STEP_NUMBER]])

        # Sort steps into groups, each set of steps that will always be executed
        # sequentially (ie. steps between branch origins and branch destinations)
        # will be put into it's own group and rendered as a singular node
        groups = extract_groups(steps)

        for (group_number, group), (next_group_number, next_group) in pairwise(groups.items()):
            # Handle special nodes if group has 1 element
            if len(group) == 1 and (step := group[0]):
                match step.opcode:
                    # Certain instructions can't be resolved into flow charts
                    case "GTI":
                        return GraphingError.BREAKING_INSTRUCTION

                    # Don't draw anything for termination instructions or unconditional branches
                    case "END" | "EXIT" | "GTO":
                        continue

                    # Draw a node for condtional branches
                    case "BIF" | "BII" | "BIN" | "BIP" | "BIT" | "BIZ":
                        graph.nodes[group_number] = Condition.from_str(step.opcode)

                        # Draw two edges for conditional branches
                        if not (len(step.operands) == 1 and isinstance(step.operands[0], int)):
                            return GraphingError.INVALID_OPERAND

                        graph.edges.append(GraphEdge(src=group_number, dst=step.operands[0], label="true"))
                        graph.edges.append(GraphEdge(src=group_number, dst=next_group_number, label="false"))
                        continue

                    # Otherwise draw a node
                    case _:
                        graph.nodes[group_number] = Group(group)

            # Otherwise insert current group
            else:
                graph.nodes[group_number] = Group(group)

            match next_group[0]:
                # If the next step is an unconditional branch, draw an edge directly to the step it branches to
                case Step("GTO", operands):
                    if not (len(operands) == 1 and isinstance(operands[0], int)):
                        return GraphingError.INVALID_OPERAND

                    graph.edges.append(GraphEdge(src=group_number, dst=operands[0]))

                # If the next step terminates the program, draw an edge to the end node
                case Step("END" | "EXIT", operands):
                    graph.edges.append(GraphEdge(src=group_number, dst=END_STEP_NUMBER))

                # Otherwise draw an edge to the next group
                case _:
                    graph.edges.append(GraphEdge(src=group_number, dst=next_group_number))

        return graph


def extract_groups(steps: dict[int, Step]) -> dict[int, list[Step]]:
    """Sort steps into sequential execution groups."""
    stack = steps.copy()
    groups = {}

    while stack:
        i = next(iter(stack.keys()))
        step = stack.pop(i)
        group = [step]

        if step.opcode not in SPECIAL_INSTRUCTIONS:
            i_next = i + 1

            # Grab sequentially executed steps and put them into the current group
            while i_next in stack and stack[i_next].opcode not in SPECIAL_INSTRUCTIONS:
                group.append(stack.pop(i_next))
                i_next += 1

        # Put branch destinations into their own group
        elif step.opcode in BRANCH_INSTRUCTIONS:
            if len(step.operands) == 1 and isinstance(step.operands[0], int):
                branch_destination = step.operands[0]

                # Reroute branch destinations that would terminate to the merged end step
                if steps[branch_destination].opcode in TERMINATION_INSTRUCTIONS:
                    step.operands = (END_STEP_NUMBER,)

                # Put branch destination into its own group
                elif branch_destination not in groups:
                    groups[branch_destination] = [stack.pop(branch_destination)]

        # Look for a preceding branch destination to join current group onto
        i_previous = i - 1
        if step.opcode in SPECIAL_INSTRUCTIONS:
            groups[i] = group
        elif i_previous in groups and groups[i_previous][0].opcode not in SPECIAL_INSTRUCTIONS:
            groups[i_previous].extend(group)
        else:
            groups[i] = group

    # Sort resulting groups by order of first step number
    return {i: groups[i] for i in sorted(groups.keys())}


def generate_dot(block: Calc) -> str:
    """Return DOT format graph as a str from a block."""
    match Graph.from_block(block):
        case Graph() as graph:
            return graph.to_dot().to_string()
        case GraphingError() as error:
            msg = f"GraphingError: {error.description}"
            raise RuntimeError(msg)
