import gc
import pickle
import re
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from billiard import Pool  # type: ignore
from quart import Quart

from quart_foxdata.models import (
    AccessFlag,
    Block,
    Config,
    Connection,
    Data,
    Meta,
    Parameter,
    ParameterReference,
)

# Regex pattern to match "<compound>:<block>.<parameter>" within config files
CONNECTION_RE = re.compile(r"^(?P<compound>\w*):(?P<block>\w+)\.(?P<parameter>.+)$", re.IGNORECASE | re.ASCII)


class FoxData:
    def __init__(self, app: Optional[Quart] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        app.extensions["foxdata"] = self

        assert "FOXDATA_ICC_DUMPS_PATH" in app.config
        assert "FOXDATA_DATA_PICKLE_PATH" in app.config
        assert app.config["FOXDATA_ICC_DUMPS_PATH"] is not None
        assert app.config["FOXDATA_DATA_PICKLE_PATH"] is not None

        icc_dumps_path = Path(app.config["FOXDATA_ICC_DUMPS_PATH"])
        data_pickle_path = Path(app.config["FOXDATA_DATA_PICKLE_PATH"])
        app.data = initialise_data(data_pickle_path, icc_dumps_path.glob("*/*.d"))  # type: ignore


@contextmanager
def gc_disabled():
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
                data = pickle.load(file)

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

    data = Data(tuple(sorted(blocks)))

    # Parse out connections between blocks
    for sink_block in data.blocks:
        for sink_parameter, sink_value in sink_block.config.items():
            if "." in sink_value and ":" in sink_value and (match := CONNECTION_RE.match(sink_value)):
                if source_block := data.get_block_from_name(
                    match.group("compound") or sink_block.compound, match.group("block")
                ):
                    conn = Connection(
                        ParameterReference(source_block, match.group("parameter")),
                        ParameterReference(sink_block, sink_parameter),
                    )

                    source_block.connections.add(conn)
                    sink_block.connections.add(conn)

    return data


def parse_dump_file(path: Path) -> tuple[Block, ...]:
    """Parses dump file at path and returns tuple of Block objects."""
    with open(path, mode="r", encoding="utf-8") as file:
        return tuple(
            Block(
                config={
                    split[0].strip(): split[1].strip()
                    for line in chunk.splitlines()
                    if len(split := line.split("=", 1)) == 2
                },
                cp=path.stem,
            )
            for chunk in file.read().strip().split("\nEND\n")
        )


_PARAMS = [
    # Meta
    Parameter(Meta("COMPOUND"), "Compound", "compound in which the block is contained", AccessFlag.NONE),
    Parameter(Meta("CP"), "CP", "CP which hosts the block", AccessFlag.NONE),
    # AIN
    Parameter(Config("NAME"), "Name", "block name", AccessFlag.NONE),
    Parameter(Config("TYPE"), "Type", "block type", AccessFlag.NONE),
    Parameter(Config("DESCRP"), "Descriptor", "descriptor", AccessFlag.NONE),
    Parameter(Config("PERIOD"), "Period", "block sample time", AccessFlag.NONE),
    Parameter(Config("PHASE"), "Phase", "block execute phase", AccessFlag.NONE),
    Parameter(Config("LOOPID"), "Loop ID", "loop identifier", AccessFlag.SET),
    Parameter(Config("IOM_ID"), "FBM", "FBM identifier", AccessFlag.NONE),
    Parameter(Config("PNT_NO"), "Point", "FBM point number", AccessFlag.NONE),
    Parameter(Config("SCI"), "SCI", "signal condition index", AccessFlag.NONE),
    Parameter(Config("HSCO1"), "High Scale (O1)", "high scale, output 1", AccessFlag.NONE),
    Parameter(Config("LSCO1"), "Low Scale (O1)", "low scale, output 1", AccessFlag.NONE),
    Parameter(Config("DELTO1"), "Delta (O1)", "change delta, output 1", AccessFlag.NONE),
    Parameter(Config("EO1"), "Units (O1)", "eng units, output 1", AccessFlag.NONE),
    Parameter(Config("OSV"), "Variance", "output span variance", AccessFlag.NONE),
    Parameter(Config("EXTBLK"), "Extender", "extender block", AccessFlag.CON | AccessFlag.SET),
]

_PARAMS_DICT = {p.source.upper(): p for p in _PARAMS}

_PARAMS_INDEX = tuple((f"{p.source.upper()} {p.name.upper()} {p.description.upper()}", p) for p in _PARAMS)


def query_parameters(query: str, exclude: Iterable[Parameter] | None = None) -> list[Parameter]:
    """Get list of parameters that contain the query string (case-insensitive) in the metadata."""

    if not exclude:
        exclude = (_PARAMS_DICT["COMPOUND"], _PARAMS_DICT["NAME"])

    def _gen(q: str) -> Generator[Parameter, None, None]:
        for k, p in _PARAMS_INDEX:
            if q in k and p not in exclude:
                yield p

    return list(_gen(query.upper()))


def get_parameter(name: str) -> Parameter | None:
    """Get parameter by name (case-insensitive) if it exists."""
    return _PARAMS_DICT.get(name.upper())
