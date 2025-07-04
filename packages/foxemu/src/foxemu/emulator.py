from foxdata.models import Block

from foxemu.blocks import EmulatedBlock
from foxemu.blocks.calc.block import Calc
from foxemu.signaling import UnparsedConnection

BlockType = EmulatedBlock | Calc


class Emulator:
    compounds: dict[str, dict[str, BlockType]]
    connections_parsed: bool

    def __init__(self) -> None:
        self.compounds = {}
        self.connections_parsed = False

    def execute(self) -> None:
        """Execute each block once."""
        if not self.connections_parsed:
            self.parse_connections()
            self.connections_parsed = True

        for compound in self.compounds.values():
            for block in compound.values():
                block.execute()

    def create_block(self, block: Block) -> BlockType:
        """Create an emulated block from a block model."""
        match block.config["TYPE"]:
            case "CALC":
                return Calc.from_block(block)
            case block_type:
                description = f"Block type not supported: '{block_type}'"
                raise RuntimeError(description)

    def add_block(self, block: BlockType) -> None:
        """Add an emulated block to the emulator."""
        if block.compound not in self.compounds:
            self.compounds[block.compound] = {}

        self.compounds[block.compound][block.name] = block

    def create_and_add_block(self, block: Block) -> None:
        """Create an emulated block from a block model and add it to the emulator."""
        self.add_block(self.create_block(block))

    def parse_connections(self) -> None:
        """Process all unparsed connections for each block."""
        for compound in self.compounds.values():
            for block in compound.values():
                for attr in block.parameters_iter():
                    if isinstance(attr.inner, UnparsedConnection):
                        attr.inner = attr.inner.parse(self)
