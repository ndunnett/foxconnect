from __future__ import annotations
from itertools import count
import re
from enum import IntFlag


class Data:
    """Object to hold all Block objects, compound structures, and CP structures"""
    blocks: list[Block]
    connections: list[Connection]
    compounds: dict[str, dict[str, "Block"]]
    cps: dict[str, list[str]]

    def __init__(self):
        self.blocks = []
        self.connections = []
        self.compounds = dict()
        self.cps = dict()

    def get_block(self, compound: str, name: str) -> Block | None:
        """Find block that matches compound and name"""
        try:
            return self.compounds[compound][name]
        except:
            return None

    def query_blocks(self, query: dict[str, str]) -> list[Block]:
        """Return list of blocks that match regex patterns"""
        def f(b):
            return all(
                (k in b or k in getattr(b, "__dict__")) and re.search(v, getattr(b, k), re.IGNORECASE)
                for k, v in query.items()
            )

        return filter(f, self.blocks)


class ParameterAccessibility(IntFlag):
    NONE = 0
    CON = 1
    SET = 2


class ParameterData:
    """Holds metadata for parameter types"""
    name: str
    title: str
    description: str
    accessibility: ParameterAccessibility

    def __init__(self, name, title, description, accessibility):
        self.name = name
        self.title = title
        self.description = description
        self.accessibility = accessibility

    def dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "description": self.description,
            "accessibility": int(self.accessibility)
        }


class Block:
    """Represents configured block within the DCS"""
    id_iter = count()

    id: int
    config: dict[str, str]
    connections: set[Connection]
    compound: str
    cp: str
    name: str

    def __init__(self, config: dict[str, str]):
        """Parses config dictionary into block object"""
        if "TYPE" in config and config["TYPE"] == "COMPND":
            self.compound = config["NAME"]
            self.name = config["NAME"]
        else:
            self.compound, self.name = config["NAME"].split(":")

        self.id = next(Block.id_iter)
        self.config = config
        self.connections = set()

    def __repr__(self):
        """<compound>:<block>"""
        return f"{self.compound}:{self.name}"

    def __eq__(self, other):
        return issubclass(type(other), Block) and self.id == other.id

    def __lt__(self, other):
        return repr(self) < repr(other)

    def __hash__(self):
        return self.id

    def __contains__(self, name):
        """Tests if config contains name"""
        return name.upper() in super().__getattribute__("config")

    def __getattribute__(self, name):
        """Tries to get config attribute if it exists"""
        if name not in (d := super().__getattribute__("__dict__")) and "config" in d and (k := name.upper()) in (c := super().__getattribute__("config")):
            return c[k]
        else:
            return super().__getattribute__(name)

    def items(self) -> dict[str, str]:
        """Returns dict items of config"""
        return self.config.items()


class Connection:
    """Represents textual connection between two blocks"""
    id_iter = count()

    id: int
    source_block: Block
    source_parameter: str
    sink_block: Block
    sink_parameter: str

    def __init__(self, source_block: Block, source_parameter: str, sink_block: Block, sink_parameter: str):
        """Records source and sink for connection"""
        self.id = next(Connection.id_iter)
        self.source_block = source_block
        self.source_parameter = source_parameter
        self.sink_block = sink_block
        self.sink_parameter = sink_parameter

    def __repr__(self):
        """<compound>:<block>.<parameter> -> <compound>:<block>.<parameter>"""
        return f"{repr(self.source_block)}.{self.source_parameter} -> {repr(self.sink_block)}.{self.sink_parameter}"

    def __eq__(self, other):
        return issubclass(type(other), Connection) and self.id == other.id

    def __lt__(self, other):
        return repr(self) < repr(other)

    def __hash__(self):
        return self.id
