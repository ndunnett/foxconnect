import sys
from quart import make_response


class RecursionDepth:
    """Context manager to temporarily change max recursion depth"""

    def __init__(self, limit):
        self.limit = limit
        self.original_limit = sys.getrecursionlimit()

    def __enter__(self):
        sys.setrecursionlimit(self.limit)

    def __exit__(self):
        sys.setrecursionlimit(self.original_limit)


def to_number(x) -> int | float:
    """Cast any type to a number"""
    return float(x) if float(x) % 1 != 0 else int(float(x))


def is_number(x) -> bool:
    """Test any type to see if it can be cast to a number"""
    try:
        to_number(x)
        return True
    except ValueError:
        return False


async def serve_plain_text(content: str):
    """Serve content as plain text"""
    response = await make_response(content, 200)
    response.mimetype = "text/plain"
    return response
