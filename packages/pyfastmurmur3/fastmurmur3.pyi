"""
Thin wrapper around the Rust crate [fastmurmur3](https://crates.io/crates/fastmurmur3), which is an
implementation of the [MurmurHash3 algorithm](https://en.wikipedia.org/wiki/MurmurHash).
"""

def murmur3(content: bytes) -> int:
    """
    Fast, non-cryptographic hash function. Takes a `bytes` object and returns the hash as an `int`.

    .. code-block:: python
        from fastmurmur3 import murmur3

        foo = murmur3("bar".encode())
    """
    ...
