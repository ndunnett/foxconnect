from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag
from typing import Any

import fastmurmur3


@dataclass(frozen=True)
class Data:
    """Container to hold all Block objects and handle queries."""

    blocks: tuple[Block, ...]
    index: dict[int, Block]
    parameters: dict[str, Parameter]

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


@dataclass(frozen=True)
class Block:
    """Represents configured block within the DCS."""

    config: dict[str, str]
    meta: dict[str, Any]
    connections: set[Connection]

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


@dataclass(frozen=True)
class ParameterReference:
    """Gives a reference to a block parameter."""

    compound: str
    name: str
    parameter: str

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


@dataclass(frozen=True)
class Connection:
    """Represents textual connection between two block parameters."""

    source: ParameterReference
    sink: ParameterReference

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

    @staticmethod
    def from_str(s: str) -> AccessFlag:
        match s:
            case "con/set":
                return AccessFlag.CON | AccessFlag.SET
            case "con/no-set":
                return AccessFlag.CON
            case "no-con/set":
                return AccessFlag.SET
            case _:
                return AccessFlag.NONE

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


@dataclass(frozen=True)
class Parameter:
    """Holds metadata for parameter types."""

    source: Source
    name: str
    description: str
    access: AccessFlag

    @staticmethod
    def from_dict(source: str, attrs: dict[str, str]) -> Parameter:
        return Parameter(
            source=Config(source) if "meta" not in attrs else Meta(source),
            name=attrs["name"],
            description=attrs["description"],
            access=AccessFlag.from_str(attrs["access"]),
        )

    def __lt__(self, other: Parameter) -> bool:
        return self.name < other.name
