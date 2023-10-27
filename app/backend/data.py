import re
from pathlib import Path
import pickle
from .models import *
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from os import cpu_count


# Path definitions
BASE_PATH = Path(__file__).resolve().parent.parent.parent
ICC_GIT_PATH = BASE_PATH.parent / "icc_git_input"
DATA_PATH = BASE_PATH / "app" / "backend" / "data"
PICKLE_PATH = DATA_PATH / "data.pickle"

# Globs to find config files and compound order files
CONFIG_GLOB = ICC_GIT_PATH.glob("*/*/*.txt")
COMPOUND_ORDER_GLOB = ICC_GIT_PATH.glob("*/_compound_order.txt")

# Regex pattern to match "<compound>:<block>.<parameter>" within config files
CONNECTION_RE = re.compile(r"^(?P<compound>\w*):(?P<block>\w+)\.(?P<parameter>\w+)$", re.ASCII)

# Regex pattern to match CP name from an ECB compound name within a compound order file
CP_ECB_RE = re.compile(r"([1-6KPT][FJ]{2}\d{3})(?:_ECB\b)", re.ASCII)

# Max worker threads for multithreading
MAX_WORKERS = cpu_count()


def initialise_data() -> Data:
    """Generate/load data"""
    # Load pickled data if it exists otherwise generate and pickle data
    if PICKLE_PATH.is_file():
        with open(PICKLE_PATH, mode="rb") as file:
            data = pickle.load(file)
    else:
        data = generate_data()
        DATA_PATH.resolve().mkdir(parents=True, exist_ok=True)
        with open(PICKLE_PATH, mode="wb") as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)

    # Propagate all Connection objects to the related Block objects
    for connection in data.connections:
        connection.source_block.connections.add(connection)
        connection.sink_block.connections.add(connection)

    return data


def generate_data() -> Data:
    """Generate all pickleable data from config and order files"""
    data = Data()
    lock = Lock()

    # Use multithreading to parse config and order files
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for path in CONFIG_GLOB:
            executor.submit(parse_config_file, lock, path, data)

        for path in COMPOUND_ORDER_GLOB:
            executor.submit(parse_order_file, lock, path, data)

    # Parse Connection objects from Block objects
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for block in data.blocks:
            executor.submit(parse_block, lock, block, data)

        # Add CP metadata to Block objects
        for cp, compounds in data.cps.items():
            for compound in compounds:
                for block in data.compounds[compound].values():
                    block.cp = cp

    # Sort blocks alphabetically by compound then block name
    data.blocks.sort()

    return data


def parse_config_file(lock: Lock, path: Path, data: Data) -> ():
    """Parses config file at path and adds Block object to blocks list"""
    with open(path, mode="r", encoding="utf-8") as file:
        if (first_line := file.readline()).startswith("NAME"):
            block = Block({
                split[0].strip(): split[1].strip()
                for line in [first_line] + list(file)
                if len(split := line.split("=", 1)) == 2
            })

            with lock:
                data.blocks.append(block)
                data.compounds.setdefault(block.compound, dict())[block.name] = block


def parse_order_file(lock: Lock, path: Path, data: Data) -> ():
    """Parses compound order file at path and populates CPs dict with compound names"""
    with open(path, mode="r", encoding="utf-8") as file:
        file = file.read()

    cp = CP_ECB_RE.search(file).group(1)
    compounds = [line for line in file.split("\n") if line in data.compounds]

    with lock:
        data.cps.setdefault(cp, []).extend(compounds)


def parse_block(lock: Lock, block: Block, data: Data) -> ():
    """Parses config from Block object and adds Connection objects to connections list"""
    connections = [
        Connection(
            data.get_block(match.group("compound") or block.compound, match.group("block")),
            match.group("parameter"),
            block,
            parameter
        )
        for parameter, value in block.items()
        if ":" in value and (match := CONNECTION_RE.match(value))
    ]

    with lock:
        data.connections.extend(connections)


def define_parameters() -> list[ParameterData]:
    return [
        # Calculated
        ParameterData("CP", "Host CP", "CP which hosts the block", ParameterAccessibility.NONE),
        ParameterData("COMPOUND", "Compound", "Compound which hosts the block", ParameterAccessibility.NONE),

        # AIN
        ParameterData("NAME", "Name", "block name", ParameterAccessibility.NONE),
        ParameterData("TYPE", "Type", "block type", ParameterAccessibility.NONE),
        ParameterData("DESCRP", "Descriptor", "descriptor", ParameterAccessibility.NONE),
        ParameterData("PERIOD", "Period", "block sample time", ParameterAccessibility.NONE),
        ParameterData("PHASE", "Phase", "block execute phase", ParameterAccessibility.NONE),
        ParameterData("LOOPID", "Loop ID", "loop identifier", ParameterAccessibility.SET),
        ParameterData("IOMOPT", "FBM Option", "FBM input option", ParameterAccessibility.NONE),
        ParameterData("IOM_ID", "FBM ID", "FBM identifier", ParameterAccessibility.NONE),
        ParameterData("PNT_NO", "FBM Point", "FBM point number", ParameterAccessibility.NONE),
        ParameterData("SCI", "SCI", "signal condition index", ParameterAccessibility.NONE),
        ParameterData("HSCO1", "High Scale (O1)", "high scale, output 1", ParameterAccessibility.NONE),
        ParameterData("LSCO1", "Low Scale (O1)", "low scale, output 1", ParameterAccessibility.NONE),
        ParameterData("DELTO1", "Delta (O1)", "change delta, output 1", ParameterAccessibility.NONE),
        ParameterData("EO1", "Units (O1)", "eng units, output 1", ParameterAccessibility.NONE),
        ParameterData("OSV", "Variance", "output span variance", ParameterAccessibility.NONE),
        ParameterData("EXTBLK", "Extender", "extender block", ParameterAccessibility.CON | ParameterAccessibility.SET),
    ]
