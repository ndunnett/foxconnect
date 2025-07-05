from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from itertools import pairwise
from typing import TYPE_CHECKING

from pydot import Dot, Edge, Node

from .constants import (
    BRANCH_INSTRUCTIONS,
    BREAKING_INSTRUCTIONS,
    CONDITIONAL_BRANCHES,
    END_STEP_NUMBER,
    SPECIAL_INSTRUCTIONS,
    TERMINATION_INSTRUCTIONS,
)
from .errors import GraphingError

if TYPE_CHECKING:
    from .block import Calc, Step


@dataclass
class Group:
    group_id: int
    steps: list[Step]

    def to_node(self) -> Node:
        node_style = "rounded" if self.steps[0].opcode in ("START", *TERMINATION_INSTRUCTIONS) else ""
        node_label = "\n".join(
            " ".join([step.opcode] + [str(operand) for operand in step.operands]) for step in self.steps
        )
        return Node(
            name=f"Step {self.group_id}",
            label=node_label,
            shape="box",
            style=node_style,
            regular="false",
            fontname="Arial",
        )


class ConditionalVariant(Enum):
    BIF = auto()
    BIZ = auto()
    BII = auto()
    BIN = auto()
    BIP = auto()
    BIT = auto()

    @staticmethod
    def from_str(string: str) -> ConditionalVariant | GraphingError:  # noqa: PLR0911
        match string:
            case "BIF":
                return ConditionalVariant.BIF
            case "BIZ":
                return ConditionalVariant.BIZ
            case "BII":
                return ConditionalVariant.BII
            case "BIN":
                return ConditionalVariant.BIN
            case "BIP":
                return ConditionalVariant.BIP
            case "BIT":
                return ConditionalVariant.BIT
            case _:
                return GraphingError.INVALID_CONDITIONAL


@dataclass
class Conditional:
    group_id: int
    variant: ConditionalVariant
    operand: int

    @staticmethod
    def from_step(group_id: int, step: Step) -> Conditional | GraphingError:
        if not (len(step.operands) == 1 and isinstance(step.operands[0], int)):
            return GraphingError.INVALID_OPERAND

        variant = ConditionalVariant.from_str(step.opcode)

        if isinstance(variant, ConditionalVariant):
            return Conditional(
                group_id=group_id,
                variant=variant,
                operand=step.operands[0],
            )
        else:
            return variant

    def to_node(self) -> Node:
        match self.variant:
            case ConditionalVariant.BIF | ConditionalVariant.BIZ:
                node_label = "== 0?"
            case ConditionalVariant.BII:
                node_label = "block\ninit?"
            case ConditionalVariant.BIN:
                node_label = "< 0?"
            case ConditionalVariant.BIP:
                node_label = ">= 0?"
            case ConditionalVariant.BIT:
                node_label = "!= 0?"

        return Node(
            name=f"Step {self.group_id}",
            label=node_label,
            shape="diamond",
            regular="true",
            fixedsize="true",
            height=0.8,
            width=0.8,
            fontname="Arial",
        )


@dataclass
class Start:
    def to_node(self) -> Node:
        return Node(
            name="Start",
            label="START",
            shape="box",
            style="rounded",
            regular="false",
            fontname="Arial",
        )


@dataclass
class End:
    def to_node(self) -> Node:
        return Node(
            name="End",
            label="END",
            shape="box",
            style="rounded",
            regular="false",
            fontname="Arial",
        )


@dataclass
class Goto:
    operand: int

    @staticmethod
    def from_step(step: Step) -> Goto | GraphingError:
        if not (len(step.operands) == 1 and isinstance(step.operands[0], int)):
            return GraphingError.INVALID_OPERAND

        return Goto(operand=step.operands[0])


GraphElement = Group | Conditional | Start | End


@dataclass
class GraphEdge:
    src: int
    dst: int
    label: str = ""

    def to_edge(self) -> Edge:
        return Edge(
            src=f"Step {self.src}" if self.src != 0 else "Start",
            dst=f"Step {self.dst}" if self.dst != END_STEP_NUMBER else "End",
            label=self.label,
            dir="forward",
            fontname="Arial",
        )


class Graph:
    name: str
    nodes: list[GraphElement]
    edges: list[GraphEdge]

    def __init__(self, block: Calc) -> None:
        self.name = f"{block.compound}__{block.name}__calc"
        self.nodes = [Start(), End()]
        self.edges = []

    def to_dot(self) -> Dot:
        dot = Dot(
            self.name,
            graph_type="graph",
            rankdir="LR",
            bgcolor="transparent",
        )

        for node in self.nodes:
            dot.add_node(node.to_node())

        for edge in self.edges:
            dot.add_edge(edge.to_edge())

        return dot

    @staticmethod
    def from_block(block: Calc) -> Graph | GraphingError:
        """Parse Calc block into a logic flow graph of steps grouped by sequential execution."""
        graph = Graph(block)
        steps = block.steps.copy()

        # Sort steps into groups, each set of steps that will always be executed
        # sequentially (ie. steps between branch origins and branch destinations)
        # will be put into it's own group and rendered as a singular node
        groups = parse_steps(steps)

        if isinstance(groups, GraphingError):
            return groups

        for (group_number, group), (next_group_number, next_group) in pairwise(groups.items()):
            # Draw nodes and conditional edges
            match group:
                case Start():
                    pass
                case Group(_, steps):
                    graph.nodes.append(group)
                case Conditional(_, _, operand):
                    graph.nodes.append(group)
                    graph.edges.append(GraphEdge(src=group_number, dst=operand, label="true"))
                    graph.edges.append(GraphEdge(src=group_number, dst=next_group_number, label="false"))
                    continue
                case Goto() | End():
                    continue

            match next_group:
                # If the next step is an unconditional branch, draw an edge directly to the step it branches to
                case Goto(operand):
                    graph.edges.append(GraphEdge(src=group_number, dst=operand))
                # If the next step terminates the program, draw an edge to the end node
                case End():
                    graph.edges.append(GraphEdge(src=group_number, dst=END_STEP_NUMBER))
                # Otherwise draw an edge to the next group
                case _:
                    graph.edges.append(GraphEdge(src=group_number, dst=next_group_number))

        return graph


def parse_steps(steps: dict[int, Step]) -> dict[int, GraphElement | Goto] | GraphingError:
    """Sort steps into sequential execution groups."""
    stack = steps.copy()
    groups: dict[int, GraphElement | Goto] = {}
    groups[0] = Start()
    groups[END_STEP_NUMBER] = End()

    while stack:
        i = next(iter(stack.keys()))
        step = stack.pop(i)

        # Fail on breaking instructions
        if step.opcode in BREAKING_INSTRUCTIONS:
            return GraphingError.BREAKING_INSTRUCTION

        # Skip over termination instructions, these will be merged into a single end step
        if step.opcode in TERMINATION_INSTRUCTIONS:
            continue

        # Put branch destinations into their own group
        if step.opcode in BRANCH_INSTRUCTIONS:
            branch = Conditional.from_step(i, step) if step.opcode in CONDITIONAL_BRANCHES else Goto.from_step(step)

            if isinstance(branch, GraphingError):
                return branch

            groups[i] = branch

            # Reroute branch destinations that would terminate to the merged end step
            if steps[branch.operand].opcode in TERMINATION_INSTRUCTIONS:
                step.operands = (END_STEP_NUMBER,)

            # Put branch destination into its own group
            elif branch.operand not in groups:
                groups[branch.operand] = Group(branch.operand, [stack.pop(branch.operand)])

        else:
            group = [step]
            i_next = i + 1

            # Grab sequentially executed steps and put them into the current group
            while i_next in stack and stack[i_next].opcode not in SPECIAL_INSTRUCTIONS:
                group.append(stack.pop(i_next))
                i_next += 1

            # Look for a preceding branch destination to join current group onto
            if i - 1 in groups and (prev_group := groups[i - 1]) and isinstance(prev_group, Group):
                prev_group.steps.extend(group)
            else:
                groups[i] = Group(i, group)

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
