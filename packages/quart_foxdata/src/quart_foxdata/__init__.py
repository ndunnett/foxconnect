import gc
import pickle
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from billiard import Pool
from quart import Quart

from quart_foxdata.models import Block, Connection, Data, ParameterAccessibility, ParameterData, ParameterReference

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
        app.data = initialise_data(data_pickle_path, icc_dumps_path.glob("*/*.d"))


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


def generate_data(dump_file_glob: Generator[Path, None, None]) -> list[Block]:
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


def parse_dump_file(path: Path) -> tuple[Block]:
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


def define_parameters() -> dict[str, ParameterData]:
    parameters = [
        # Calculated
        ParameterData("CP", "CP", "CP which hosts the block", ParameterAccessibility.NONE),
        # AIN
        ParameterData("NAME", "Name", "block name", ParameterAccessibility.NONE),
        ParameterData("TYPE", "Type", "block type", ParameterAccessibility.NONE),
        ParameterData("DESCRP", "Descriptor", "descriptor", ParameterAccessibility.NONE),
        ParameterData("PERIOD", "Period", "block sample time", ParameterAccessibility.NONE),
        ParameterData("PHASE", "Phase", "block execute phase", ParameterAccessibility.NONE),
        ParameterData("LOOPID", "Loop ID", "loop identifier", ParameterAccessibility.SET),
        ParameterData("IOM_ID", "FBM", "FBM identifier", ParameterAccessibility.NONE),
        ParameterData("PNT_NO", "Point", "FBM point number", ParameterAccessibility.NONE),
        ParameterData("SCI", "SCI", "signal condition index", ParameterAccessibility.NONE),
        ParameterData("HSCO1", "High Scale (O1)", "high scale, output 1", ParameterAccessibility.NONE),
        ParameterData("LSCO1", "Low Scale (O1)", "low scale, output 1", ParameterAccessibility.NONE),
        ParameterData("DELTO1", "Delta (O1)", "change delta, output 1", ParameterAccessibility.NONE),
        ParameterData("EO1", "Units (O1)", "eng units, output 1", ParameterAccessibility.NONE),
        ParameterData("OSV", "Variance", "output span variance", ParameterAccessibility.NONE),
        ParameterData("EXTBLK", "Extender", "extender block", ParameterAccessibility.CON | ParameterAccessibility.SET),
    ]

    return {p.name: p for p in parameters}
