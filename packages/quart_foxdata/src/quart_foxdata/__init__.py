import pickle
import re
from collections.abc import Generator, Iterable
from functools import lru_cache
from pathlib import Path

from quart import Quart, current_app

from quart_foxdata.models import Block, Data, Parameter, ParameterReference
from quart_foxdata.parsing import generate_data
from quart_foxdata.util import filter_map, gc_disabled


class FoxData:
    def __init__(self, app: Quart | None = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        app.extensions["foxdata"] = self

        for conf in ("FOXDATA_ICC_DUMPS_PATH", "FOXDATA_DATA_PICKLE_PATH"):
            if conf not in app.config or app.config[conf] is None:
                raise RuntimeError(f"Configuration key '{conf}' not set")

        icc_dumps_path = Path(app.config["FOXDATA_ICC_DUMPS_PATH"])
        data_pickle_path = Path(app.config["FOXDATA_DATA_PICKLE_PATH"])
        app.data = initialise_data(data_pickle_path, icc_dumps_path.glob("*/*.d"))  # type: ignore


def initialise_data(data_pickle_path: Path, dump_file_glob: Generator[Path, None, None]) -> Data:
    """Load pickled data if it exists otherwise generate and pickle data."""
    with gc_disabled():
        if data_pickle_path.is_file() and False:
            with open(data_pickle_path, mode="rb") as file:
                data = pickle.load(file)  # noqa: S301

        else:
            data = generate_data(dump_file_glob)
            data_pickle_path.parent.resolve().mkdir(parents=True, exist_ok=True)

            with open(data_pickle_path, mode="wb") as file:
                pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    return data


def get_data() -> Data:
    return current_app.data  # type: ignore


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
