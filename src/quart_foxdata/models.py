from __future__ import annotations

import re
from collections.abc import Iterable
from enum import IntFlag
from functools import lru_cache
from typing import Any, Callable, Generator, Optional

import fastmurmur3


def is_stringable(x: Any) -> bool:
    """Test any type to see if it can be cast to a string."""
    try:
        str(x)
        return True
    except TypeError:
        return False


def filter_map[T, U](func: Callable[[T], Optional[U]], it: Iterable[T]) -> Generator[U, None, None]:
    """Maps function over iterator and yields results that are not None."""
    for element in it:
        if (result := func(element)) is not None:
            yield result


class Data:
    """Container to hold all Block objects and handle queries."""

    __slots__ = ("blocks", "index")
    blocks: tuple[Block]
    index: dict[int, Block]
    hasher: Callable[[str], int] = fastmurmur3.hash

    def __init__(self, blocks: tuple[Block]):
        self.blocks = blocks
        self.index = {hash(block): block for block in blocks}

    def get_block_from_name(self, compound: str, name: str) -> Optional[Block]:
        """Search index for given compound and block name."""
        return self.get_block_from_hash(Data.hasher(f"{compound}:{name}"))

    def get_block_from_ref(self, parameter_reference: ParameterReference) -> Optional[Block]:
        """Search index for block in given parameter reference."""
        return self.get_block_from_hash(parameter_reference.block_hash)

    def get_block_from_hash(self, block_hash: int) -> Optional[Block]:
        """Search index for block in given block hash."""
        if block_hash in self.index:
            return self.index[block_hash]
        else:
            return None

    @lru_cache
    def query_blocks(self, query: tuple[tuple[str, str]]) -> list[dict[str, str]]:
        """Return list of block data dicts that match query."""
        filters = tuple((key, re.compile(pattern, re.IGNORECASE | re.ASCII)) for key, pattern in query if pattern)

        def _f(block: Block) -> Optional[dict[str, str]]:
            if all(is_stringable(block[key]) and pattern.search(str(block[key])) for key, pattern in filters):
                return {key: block[key] for key, _ in query}
            else:
                return None

        return list(filter_map(_f, self.blocks))


class Block:
    """Represents configured block within the DCS."""

    __slots__ = ("config", "meta", "connections")
    config: dict[str, str]
    meta: dict[str, Any]
    connections: set[Connection]

    def __init__(self, config: dict[str, str], **meta: dict[str, Any]):
        """Parses config dictionary into block object."""
        if "TYPE" in config and config["TYPE"] == "COMPND":
            compound, name = config["NAME"], config["NAME"]
        else:
            compound, name = config["NAME"].split(":")

        self.config = config
        self.meta = {"compound": compound, "name": name} | meta
        self.connections = set()

    def __repr__(self) -> str:
        """<compound>:<block>"""
        return f"{self.compound}:{self.name}"

    def __eq__(self, other: Block) -> bool:
        return hash(self) == hash(other)

    def __lt__(self, other: Block) -> bool:
        return repr(self.compound) < repr(other.compound)

    def __hash__(self) -> int:
        return Data.hasher(repr(self))

    def __getitem__(self, name: str) -> Optional[Any]:
        if (k := name.lower()) in self.meta:
            return self.meta[k]
        elif (k := name.upper()) in self.config:
            return self.config[k]
        else:
            return None

    @property
    def name(self) -> str:
        return self.meta["name"]

    @property
    def compound(self) -> str:
        return self.meta["compound"]

    def list_connections(self) -> list[tuple[bool, str, ParameterReference]]:
        def f(c: Connection) -> tuple[Connection, bool]:
            if c.sink.name == self.name and c.sink.compound == self.compound:
                return (False, c.sink.parameter, c.source)
            else:
                return (True, c.source.parameter, c.sink)

        return sorted(map(f, self.connections))


class ParameterReference:
    """Gives a reference to a block parameter."""

    __slots__ = ("compound", "name", "parameter")
    compound: str
    name: str
    parameter: str

    def __init__(self, block: Block, parameter: str):
        self.compound = block.compound
        self.name = block.name
        self.parameter = parameter

    def __repr__(self) -> str:
        """<compound>:<block>.<parameter>"""
        return f"{self.compound}:{self.name}.{self.parameter}"

    def __lt__(self, other: ParameterReference) -> bool:
        return repr(self) < repr(other)

    @property
    def block_hash(self) -> int:
        return Data.hasher(f"{self.compound}:{self.name}")

    def matches_block(self, block: Block) -> bool:
        return self.compound == block.compound and self.name == block.name


class Connection:
    """Represents textual connection between two block parameters."""

    __slots__ = ("source", "sink")
    source: ParameterReference
    sink: ParameterReference

    def __init__(self, source: ParameterReference, sink: ParameterReference):
        self.source = source
        self.sink = sink

    def __repr__(self) -> str:
        """<source> --> <sink>"""
        return f"{repr(self.source)} --> {repr(self.sink)}"

    def __lt__(self, other: Connection) -> bool:
        return repr(self) < repr(other)


class ParameterAccessibility(IntFlag):
    NONE = 0
    CON = 1
    SET = 2


class ParameterData:
    """Holds metadata for parameter types."""

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
        return {"title": self.title, "description": self.description, "accessibility": int(self.accessibility)}
