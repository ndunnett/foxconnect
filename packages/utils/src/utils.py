import gc
import math
import subprocess
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class Stringable(Protocol):
    """Protocol for types that support being cast to a string."""

    def __str__(self) -> str: ...


@runtime_checkable
class SupportsMaths[X, Y](Protocol):
    """Protocol for types that support mathematical operations."""

    def __add__(self, x: X, /) -> Y: ...
    def __sub__(self, x: X, /) -> Y: ...
    def __mul__(self, x: X, /) -> Y: ...


@runtime_checkable
class SupportsRichComparison[T](Protocol):
    """Protocol for types that support rich comparison."""

    def __lt__(self, other: T, /) -> bool: ...
    def __gt__(self, other: T, /) -> bool: ...


def maybe_float(s: str) -> str | float:
    """Convert string to a float if it is a number."""
    try:
        return float(s)
    except ValueError:
        return s


def truncate_number(x: float, sig_figs: int) -> float:
    """Truncate number to a specific amount of significant figures."""
    if (x * sig_figs) % 1 == 0:
        return float(x)
    else:
        shift = 10 ** (sig_figs - math.ceil(math.log10(abs(x))))
        return round(x * shift, 0) / shift


def clamp[N: SupportsRichComparison](x: N, low: N, high: N) -> N:
    """Clamp number between low and high."""
    return max(low, min(high, x))


@contextmanager
def gc_disabled() -> Generator[None]:
    """Context manager to temporarily disable garbage collection. Does nothing if already disabled."""
    enabled = gc.isenabled()

    try:
        yield gc.disable() if enabled else None
    finally:
        if enabled:
            gc.enable()


def filter_map[X, Y](function: Callable[[X], Y | None], iterable: Iterable[X]) -> Generator[Y]:
    """Map a function over an iterable and yield results that are not `None`."""
    for element in iterable:
        if (result := function(element)) is not None:
            yield result


def yarn_install(package_path: Path | None = None, node_modules_link: Path | None = None) -> None:
    """
    Run `yarn install` as a subprocess and optionally set a symbolic link to node_modules.

    Expects yarn to be available locally, only works on Unix based operating systems.
    """
    subprocess.run(
        args="y | yarn install",
        cwd=package_path,
        shell=True,
        check=True,
    )

    if package_path and node_modules_link:
        node_modules_link.symlink_to(package_path / "node_modules", target_is_directory=True)
