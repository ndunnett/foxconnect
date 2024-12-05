"""
This module is a thin wrapper around the Rust crate [fastmurmur3](https://crates.io/crates/fastmurmur3) which is an
implementation of the [MurmurHash3 algorithm](https://en.wikipedia.org/wiki/MurmurHash).
"""

def hash(text: str) -> int:  # noqa: A001
    """Fast, non-cryptographic hash function.

    .. code-block:: python
        foo = fastmurmur3.hash("bar")
    """
    ...
