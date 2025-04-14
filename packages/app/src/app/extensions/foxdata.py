import re
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from foxdata import initialise_data
from foxdata.models import Block, Data, Parameter, ParameterReference
from quart import Quart, current_app
from utils import filter_map


class FoxData:
    """This is a Quart extension to handle the data for the application.

    ICC dumps are parsed and pickled according to `FOXDATA_ICC_DUMPS_PATH` and
    `FOXDATA_DATA_PICKLE_PATH` configuration values.
    """

    data: Data

    def __init__(self, app: Quart | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        """Initialises the extension for a given Quart instance.

        * Registers the extension with the app
        * Initialises the data object
        """

        app.extensions["foxdata"] = self

        for conf in ("FOXDATA_ICC_DUMPS_PATH", "FOXDATA_DATA_PICKLE_PATH"):
            if conf not in app.config or app.config[conf] is None:
                raise RuntimeError(f"Configuration key '{conf}' not set")

        icc_dumps_path = Path(app.config["FOXDATA_ICC_DUMPS_PATH"])
        data_pickle_path = Path(app.config["FOXDATA_DATA_PICKLE_PATH"])
        self.data = initialise_data(data_pickle_path, icc_dumps_path.glob("*/*.d"))


def get_data() -> Data:
    """Fetch data object from the global current app."""
    return current_app.extensions["foxdata"].data


def get_parameter(name: str) -> Parameter | None:
    """Get parameter by name (case-insensitive) if it exists."""
    return get_data().parameters.get(name.upper())


def get_block_from_name(compound: str, name: str) -> Block | None:
    """Search index for given compound and block name."""
    return get_data().get_block_from_name(compound, name)


def get_block_from_ref(parameter_reference: ParameterReference) -> Block | None:
    """Search index for block in given parameter reference."""
    return get_data().get_block_from_ref(parameter_reference)


def get_block_from_hash(block_hash: int) -> Block | None:
    """Search index for block in given block hash."""
    return get_data().get_block_from_hash(block_hash)


@lru_cache
def query_blocks(query: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    """Return list of block data dicts that match query."""
    filters = tuple((key, re.compile(pattern, re.IGNORECASE | re.ASCII)) for key, pattern in query if pattern)

    def _f(block: Block) -> dict[str, str] | None:
        if all(pattern.search(str(block[key])) for key, pattern in filters):
            return {key: str(block[key] or "") for key, _ in query}
        else:
            return None

    return list(filter_map(_f, get_data().blocks))


def query_parameters(query: str, exclude: Iterable[str] | None = None) -> list[Parameter]:
    """Return list of parameters that contain the query string (case-insensitive) in the metadata."""

    if not exclude:
        exclude = ("COMPOUND", "NAME")

    return [
        p
        for p in get_data().parameters.values()
        if p.source not in exclude and query.upper() in f".{p.source.upper()} {p.name.upper()} {p.description.upper()}"
    ]
