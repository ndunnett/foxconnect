import cython


def djb2_hash(text: str) -> int:
    """Implementation of the k=33 XOR hashing algorithm by Dan Bernstein."""
    # http://www.cse.yorku.ca/~oz/hash.html
    buffer: bytes = text.encode()
    digest: cython.int = 0x1505
    ch: cython.int

    for ch in buffer:
        digest = (digest << 5) + digest + ch

    return digest
