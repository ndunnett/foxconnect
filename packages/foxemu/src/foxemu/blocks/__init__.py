from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

    from foxemu.signaling import Parameter


class EmulatedBlock:
    """Base object for emulated blocks."""

    compound: str
    name: str

    def __init__(self, compound: str, name: str) -> None:
        self.compound = compound
        self.name = name

    def __repr__(self) -> str:
        return f"{self.__qualname__}({self.compound}:{self.name})"

    def __str__(self) -> str:
        return f"{self.compound}:{self.name}"

    def parameters_iter(self) -> Generator[Parameter]:
        """Iterate over block parameters."""
        raise GeneratorExit

    def get_parameter(self, _key: str) -> Parameter | None:
        """Get block parameter by name."""
        raise RuntimeError

    def execute(self) -> None:
        """Execute the block once."""
        pass
