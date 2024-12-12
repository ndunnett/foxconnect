import gc
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager


@contextmanager
def gc_disabled() -> Generator[None, None, None]:
    """Context manager to temporarily disable garbage collection."""
    try:
        yield gc.disable()
    finally:
        gc.enable()


def filter_map[X, Y](func: Callable[[X], Y | None], it: Iterable[X]) -> Generator[Y]:
    """Maps function over iterator and yields results that are not None."""
    for element in it:
        if (result := func(element)) is not None:
            yield result
