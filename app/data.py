import re
from pathlib import Path
import pickle
from multiprocessing import Pool
from typing import Generator
from app.models import *


# Path definitions
BASE_PATH = Path(__file__).resolve().parent.parent
ICC_DUMPS_PATH = BASE_PATH.parent / "icc_dumps"
DATA_PATH = BASE_PATH / "data"
PICKLE_PATH = DATA_PATH / "data.pickle"

# Globs to find CP dump files
DUMP_FILE_GLOB = ICC_DUMPS_PATH.glob("*/*.d")

# Regex pattern to match "<compound>:<block>.<parameter>" within config files
CONNECTION_RE = re.compile(r"^(?P<compound>\w*):(?P<block>\w+)\.(?P<parameter>.+)$", re.IGNORECASE | re.ASCII)


def initialise_data() -> Data:
    """Generate/load data."""
    # Load pickled data if it exists otherwise generate and pickle data
    if PICKLE_PATH.is_file():
        with open(PICKLE_PATH, mode="rb") as file:
            data = pickle.load(file)
    else:
        data = generate_data(DUMP_FILE_GLOB)
        DATA_PATH.resolve().mkdir(parents=True, exist_ok=True)
        with open(PICKLE_PATH, mode="wb") as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    return data


def generate_data(dump_file_glob: Generator[Path, None, None]) -> Data:
    """Generate all pickleable data from config and order files."""
    # Use process pool to concurrently parse blocks from dump files
    with Pool() as pool:
        futures = [pool.apply_async(parse_dump_file, [path]) for path in dump_file_glob]
        blocks = [block for future in futures for block in future.get()]

    data = Data(sorted(blocks))

    # Parse out connections between blocks
    for sink_block in data.blocks:
        for sink_parameter, sink_value in sink_block.config.items():
            if "." in sink_value and ":" in sink_value and (match := CONNECTION_RE.match(sink_value)):
                if source_block := data.get_block_from_name(match.group("compound") or sink_block.compound, match.group("block")):
                    conn = Connection(
                        ParameterReference(source_block, match.group("parameter")),
                        ParameterReference(sink_block, sink_parameter),
                    )

                    source_block.connections.add(conn)
                    sink_block.connections.add(conn)

    return data


def parse_dump_file(path: Path) -> list[Block]:
    """Parses dump file at path and adds Block object to blocks list."""
    with open(path, mode="r", encoding="utf-8") as file:
        return [
            Block(config={
                split[0].strip(): split[1].strip()
                for line in chunk.splitlines()
                if len(split := line.split("=", 1)) == 2
            }, meta={
                "cp": path.stem,
            })
            for chunk in file.read().strip().split("\nEND\n")
        ]


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
