import gc
import subprocess
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager
from pathlib import Path


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
    """Maps function over iterable and yields results that are not None."""
    for element in iterable:
        if (result := function(element)) is not None:
            yield result


def maybe_float(s: str) -> str | float:
    """Convert string to a float if it is a number."""
    try:
        return float(s)
    except ValueError:
        return s


def yarn_install(package_path: Path | None = None, node_modules_link: Path | None = None) -> None:
    """
    Runs `yarn install` as a subprocess and optionally sets a symbolic link to node_modules.
    Expects yarn to be available locally.
    """

    subprocess.run(
        args="y | yarn install",
        cwd=package_path,
        shell=True,
        check=True,
    )

    if package_path and node_modules_link:
        node_modules_link.symlink_to(package_path / "node_modules", target_is_directory=True)
