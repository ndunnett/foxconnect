from __future__ import annotations
from itertools import count


class Data:
    """Object to hold all Block objects, compound structures, and CP structures"""
    blocks: list[Block]
    connections: list[Connection]
    compounds = dict[str, dict[str, "Block"]]
    cps = dict[str, list[str]]

    def __init__(self):
        self.blocks = []
        self.connections = []
        self.compounds = dict()
        self.cps = dict()

    def find_block(self, compound, name) -> Block | None:
        """Find block that matches compound and name"""
        return self.compounds[compound][name] or None

    def get_structure(self) -> dict[str, list[Block]]:
        """Return dictionary of compounds, each key containing a list of block names"""
        structure = dict()

        for block in self.blocks:
            structure.setdefault(block.compound, []).append(block.name)

        return structure


class UniqueHashable:
    """Base class for unique hashable objects"""
    id_iter = count()

    def __eq__(self, other):
        return issubclass(type(other), UniqueHashable) and self.id == other.id

    def __lt__(self, other):
        return repr(self) < repr(other)

    def __hash__(self):
        return self.id


class Block(UniqueHashable):
    """Represents configured block within the DCS"""
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

        self.id = next(UniqueHashable.id_iter)
        self.config = config
        self.connections = set()

    def __repr__(self):
        """<compound>:<block>"""
        return f"{self.compound}:{self.name}"

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


class Connection(UniqueHashable):
    """Represents textual connection between two blocks"""
    id: int
    source_block: Block
    source_parameter: str
    sink_block: Block
    sink_parameter: str

    def __init__(self, source_block: Block, source_parameter: str, sink_block: Block, sink_parameter: str):
        """Records source and sink for connection"""
        self.id = next(UniqueHashable.id_iter)
        self.source_block = source_block
        self.source_parameter = source_parameter
        self.sink_block = sink_block
        self.sink_parameter = sink_parameter

    def __repr__(self):
        """<compound>:<block>.<parameter> -> <compound>:<block>.<parameter>"""
        return f"{repr(self.source_block)}.{self.source_parameter} -> {repr(self.sink_block)}.{self.sink_parameter}"
