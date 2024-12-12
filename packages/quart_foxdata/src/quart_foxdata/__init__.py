import gc
import importlib.resources
import pickle
import re
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import yaml
from billiard import Pool  # type: ignore
from quart import Quart

from quart_foxdata.models import Block, Connection, Data, Parameter, ParameterReference

# Regex pattern to match "<compound>:<block>.<parameter>" within config files
CONNECTION_RE = re.compile(r"^(?P<compound>\w*):(?P<block>\w+)\.(?P<parameter>.+)$", re.IGNORECASE | re.ASCII)


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


@contextmanager
def gc_disabled() -> Generator[None, None, None]:
    """Context manager to temporarily disable garbage collection."""
    try:
        yield gc.disable()
    finally:
        gc.enable()


def initialise_data(data_pickle_path: Path, dump_file_glob: Generator[Path, None, None]) -> Data:
    """Load pickled data if it exists otherwise generate and pickle data."""
    with gc_disabled():
        if data_pickle_path.is_file():
            with open(data_pickle_path, mode="rb") as file:
                data = pickle.load(file)  # noqa: S301

        else:
            data = generate_data(dump_file_glob)
            data_pickle_path.parent.resolve().mkdir(parents=True, exist_ok=True)

            with open(data_pickle_path, mode="wb") as file:
                pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    return data


def generate_data(dump_file_glob: Generator[Path, None, None]) -> Data:
    """Parse all CP dump files to create a Data object containing parsed blocks."""
    # Use process pool to concurrently parse blocks from dump files
    with Pool() as pool:
        blocks = [block for result in pool.map(parse_dump_file, dump_file_glob) for block in result]

    data = Data(tuple(sorted(blocks)), parse_parameters())

    # Parse out connections between blocks
    for sink_block in data.blocks:
        for sink_parameter, sink_value in sink_block.config.items():
            if "." not in sink_value or ":" not in sink_value:
                continue

            match = CONNECTION_RE.match(sink_value)

            if match is None:
                continue

            source_block = data.get_block_from_name(
                match.group("compound") or sink_block.compound,
                match.group("block"),
            )

            if source_block is None:
                continue

            conn = Connection(
                ParameterReference(source_block, match.group("parameter")),
                ParameterReference(sink_block, sink_parameter),
            )

            source_block.connections.add(conn)
            sink_block.connections.add(conn)

    return data


def parse_dump_file(path: Path) -> tuple[Block, ...]:
    """Parses dump file at path and returns tuple of Block objects."""
    with open(path, encoding="utf-8") as file:
        return tuple(
            Block(
                config={
                    split[0].strip(): split[1].strip()
                    for line in chunk.splitlines()
                    if len(split := line.split("=", 1)) == 2  # noqa: PLR2004
                },
                cp=path.stem,
            )
            for chunk in file.read().strip().split("\nEND\n")
        )


def parse_parameters() -> dict[str, Parameter]:
    """Parses parameter metadata from YAML file."""
    with (importlib.resources.files("quart_foxdata") / "parameters.yaml").open() as file:
        data = yaml.safe_load(file)

    return {p.source: p for k, v in data.items() if (p := Parameter.from_dict(k, v))}
