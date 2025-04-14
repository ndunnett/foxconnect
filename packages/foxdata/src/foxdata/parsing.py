import importlib.resources
import re
from collections.abc import Iterator
from pathlib import Path

import yaml
from billiard import Pool  # type: ignore

from .models import Block, Connection, Data, Parameter, ParameterReference

# Regex pattern to match "<compound>:<block>.<parameter>" within config files
CONNECTION_RE = re.compile(r"^(?P<compound>\w*):(?P<block>\w+)\.(?P<parameter>.+)$", re.IGNORECASE | re.ASCII)


def generate_data(dump_file_glob: Iterator[Path]) -> Data:
    """Parse all CP dump files to create a Data object containing parsed blocks."""
    # Use process pool to concurrently parse blocks from dump files
    with Pool() as pool:
        blocks = tuple(sorted(block for result in pool.map(parse_dump_file, dump_file_glob) for block in result))

    block_index = {hash(block): block for block in blocks}
    parameters = parse_parameters()
    data = Data(blocks, block_index, parameters)

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
                ParameterReference(source_block.compound, source_block.name, match.group("parameter")),
                ParameterReference(sink_block.compound, sink_block.name, sink_parameter),
            )

            source_block.connections.add(conn)
            sink_block.connections.add(conn)

    return data


def parse_dump_file(path: Path) -> tuple[Block, ...]:
    """Parses dump file at path and returns tuple of Block objects."""
    with open(path, encoding="utf-8") as file:
        return tuple(parse_block(chunk, path) for chunk in file.read().strip().split("\nEND\n"))


def parse_block(chunk: str, path: Path) -> Block:
    """Parses chunk from a config file into a Block object."""

    config = {
        split[0].strip(): split[1].strip()
        for line in chunk.splitlines()
        if len(split := line.split("=", 1)) == 2  # noqa: PLR2004
    }

    if "TYPE" in config and config["TYPE"] == "COMPND":
        compound, name = config["NAME"], config["NAME"]
    else:
        compound, name = config["NAME"].split(":")

    meta = {"compound": compound, "name": name, "cp": path.stem}
    connections = set()

    return Block(config, meta, connections)


def parse_parameters() -> dict[str, Parameter]:
    """Parses parameter metadata from YAML file."""
    with (importlib.resources.files("foxdata") / "parameters.yaml").open() as file:
        data = yaml.safe_load(file)

    return {p.source: p for k, v in data.items() if (p := Parameter.from_dict(k, v))}
