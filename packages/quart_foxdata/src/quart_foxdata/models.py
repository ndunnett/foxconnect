from __future__ import annotations

import re
from enum import IntFlag
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import fastmurmur3

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable


def filter_map[X, Y](func: Callable[[X], Y | None], it: Iterable[X]) -> Generator[Y]:
    """Maps function over iterator and yields results that are not None."""
    for element in it:
        if (result := func(element)) is not None:
            yield result


class Data:
    """Container to hold all Block objects and handle queries."""

    __slots__ = ("blocks", "index")
    blocks: tuple[Block, ...]
    index: dict[int, Block]

    def __init__(self, blocks: tuple[Block, ...]) -> None:
        self.blocks = blocks
        self.index = {hash(block): block for block in blocks}

    def get_block_from_name(self, compound: str, name: str) -> Block | None:
        """Search index for given compound and block name."""
        return self.get_block_from_hash(fastmurmur3.hash(f"{compound}:{name}"))

    def get_block_from_ref(self, parameter_reference: ParameterReference) -> Block | None:
        """Search index for block in given parameter reference."""
        return self.get_block_from_hash(parameter_reference.block_hash)

    def get_block_from_hash(self, block_hash: int) -> Block | None:
        """Search index for block in given block hash."""
        if block_hash in self.index:
            return self.index[block_hash]
        else:
            return None

    @lru_cache  # noqa: B019
    def query_blocks(self, query: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
        """Return list of block data dicts that match query."""
        filters = tuple((key, re.compile(pattern, re.IGNORECASE | re.ASCII)) for key, pattern in query if pattern)

        def _f(block: Block) -> dict[str, str] | None:
            if all(pattern.search(str(block[key])) for key, pattern in filters):
                return {key: str(block[key] or "") for key, _ in query}
            else:
                return None

        return list(filter_map(_f, self.blocks))


class Block:
    """Represents configured block within the DCS."""

    __slots__ = ("config", "connections", "meta")
    config: dict[str, str]
    meta: dict[str, Any]
    connections: set[Connection]

    def __init__(self, config: dict[str, str], **meta: Any) -> None:
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Block):
            return hash(self) == hash(other)
        else:
            return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Block):
            return repr(self.compound) < repr(other.compound)
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return fastmurmur3.hash(repr(self))

    def __getitem__(self, name: str) -> Any | None:
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
        def f(c: Connection) -> tuple[bool, str, ParameterReference]:
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

    def __init__(self, block: Block, parameter: str) -> None:
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
        return fastmurmur3.hash(f"{self.compound}:{self.name}")

    def matches_block(self, block: Block) -> bool:
        return self.compound == block.compound and self.name == block.name


class Connection:
    """Represents textual connection between two block parameters."""

    __slots__ = ("sink", "source")
    source: ParameterReference
    sink: ParameterReference

    def __init__(self, source: ParameterReference, sink: ParameterReference) -> None:
        self.source = source
        self.sink = sink

    def __repr__(self) -> str:
        """<source> --> <sink>"""
        return f"{self.source!r} --> {self.sink!r}"

    def __lt__(self, other: Connection) -> bool:
        return repr(self) < repr(other)


class AccessFlag(IntFlag):
    """Represents permissible access to a block parameter."""

    NONE = 0
    CON = 1
    SET = 2

    def __str__(self) -> str:
        if AccessFlag.CON | AccessFlag.SET in self:
            return "con/set"
        elif AccessFlag.CON in self:
            return "con/no-set"
        elif AccessFlag.SET in self:
            return "no-con/set"
        else:
            return "no-con/no-set"


class Meta(str): ...  # noqa: SLOT000


class Config(str): ...  # noqa: SLOT000


Source = Meta | Config


class Parameter:
    """Holds metadata for parameter types."""

    source: Source
    name: str
    description: str
    access: AccessFlag

    def __init__(self, source: Source, name: str, description: str, access: AccessFlag) -> None:
        self.source = source
        self.name = name
        self.description = description
        self.access = access

    def search_line(self) -> str:
        return f"{self.source}\t{self.name}\t{self.description}"
