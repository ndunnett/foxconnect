from typing import Any, Callable, Generator
from collections.abc import Iterable
import sys
import gc
from quart import make_response
from contextlib import contextmanager


@contextmanager
def gc_disabled():
    """Context manager to temporarily disable garbage collection."""
    try:
        yield gc.disable()
    finally:
        gc.enable()


@contextmanager
def recursion_depth(limit: int):
    """Context manager to temporarily change max recursion depth."""
    try:
        original_limit = sys.getrecursionlimit()
        yield sys.setrecursionlimit(limit)
    finally:
        sys.setrecursionlimit(original_limit)


def to_number(x: Any) -> int | float:
    """Cast any type to a number."""
    return float(x) if float(x) % 1 != 0 else int(float(x))


def is_number(x: Any) -> bool:
    """Test any type to see if it can be cast to a number."""
    try:
        to_number(x)
        return True
    except ValueError:
        return False


def is_stringable(x: Any) -> bool:
    """Test any type to see if it can be cast to a string."""
    try:
        str(x)
        return True
    except TypeError:
        return False


async def serve_plain_text(content: str):
    """Serve content as plain text."""
    response = await make_response(content, 200)
    response.mimetype = "text/plain"
    return response


def filter_map[T, U](func: Callable[[T], U | None], it: Iterable[T]) -> Generator[U, None, None]:
    """Maps function over iterator and yields results that are not None."""
    for element in it:
        if (result := func(element)) is not None:
            yield result
