# ruff: noqa: FBT003
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from foxdata.parsing import CONNECTION_RE

from foxemu.signaling import (
    BoolValue,
    Input,
    IntegerValue,
    LongValue,
    Output,
    Parameter,
    RealValue,
    ShortValue,
    StringValue,
    UnparsedConnection,
)

if TYPE_CHECKING:
    from foxdata.models import Block


@dataclass
class CalcParameters:
    """CALC block parameters."""

    NAME: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    TYPE: Parameter[IntegerValue] = field(default_factory=lambda: Parameter(IntegerValue(18)))
    DESCRP: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    PERIOD: Parameter[ShortValue] = field(default_factory=lambda: Parameter(ShortValue(1)))
    PHASE: Parameter[IntegerValue] = field(default_factory=lambda: Parameter(IntegerValue(0)))
    LOOPID: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    MA: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    INITMA: Parameter[ShortValue] = field(default_factory=lambda: Parameter(ShortValue(1)))
    TIMINI: Parameter[ShortValue] = field(default_factory=lambda: Parameter(ShortValue(0)))
    BLKSTA: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    PERROR: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    STERR: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))

    RI01: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI02: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI03: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI04: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI05: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI06: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI07: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    RI08: Input[RealValue] = field(default_factory=lambda: Input(RealValue(0)))
    HSCI1: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI2: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI3: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI4: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI5: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI6: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI7: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCI8: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    LSCI1: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI2: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI3: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI4: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI5: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI6: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI7: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCI8: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    DELTI1: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI2: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI3: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI4: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI5: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI6: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI7: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    DELTI8: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(1)))
    EI1: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI2: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI3: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI4: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI5: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI6: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI7: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EI8: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    BI01: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI02: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI03: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI04: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI05: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI06: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI07: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI08: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI09: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI10: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI11: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI12: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI13: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI14: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI15: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    BI16: Input[BoolValue] = field(default_factory=lambda: Input(BoolValue(False)))
    II01: Input[IntegerValue] = field(default_factory=lambda: Input(IntegerValue(0)))
    II02: Input[IntegerValue] = field(default_factory=lambda: Input(IntegerValue(0)))
    LI01: Input[LongValue] = field(default_factory=lambda: Input(LongValue(0)))
    LI02: Input[LongValue] = field(default_factory=lambda: Input(LongValue(0)))

    RO01: Output[RealValue] = field(default_factory=lambda: Output(RealValue(0)))
    RO02: Output[RealValue] = field(default_factory=lambda: Output(RealValue(0)))
    RO03: Output[RealValue] = field(default_factory=lambda: Output(RealValue(0)))
    RO04: Output[RealValue] = field(default_factory=lambda: Output(RealValue(0)))
    HSCO1: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCO2: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCO3: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    HSCO4: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(100)))
    LSCO1: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCO2: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCO3: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    LSCO4: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    EO1: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EO2: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EO3: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    EO4: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("%")))
    BO01: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO02: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO03: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO04: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO05: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO06: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO07: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    BO08: Output[BoolValue] = field(default_factory=lambda: Output(BoolValue(False)))
    IO01: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    IO02: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    IO03: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    IO04: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    IO05: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    IO06: Output[IntegerValue] = field(default_factory=lambda: Output(IntegerValue(0)))
    LO01: Output[LongValue] = field(default_factory=lambda: Output(LongValue(0)))
    LO02: Output[LongValue] = field(default_factory=lambda: Output(LongValue(0)))

    M01: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M02: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M03: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M04: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M05: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M06: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M07: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M08: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M09: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M10: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M11: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M12: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M13: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M14: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M15: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M16: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M17: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M18: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M19: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M20: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M21: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M22: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M23: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))
    M24: Parameter[RealValue] = field(default_factory=lambda: Parameter(RealValue(0)))

    STEP01: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP02: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP03: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP04: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP05: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP06: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP07: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP08: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP09: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP10: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP11: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP12: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP13: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP14: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP15: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP16: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP17: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP18: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP19: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP20: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP21: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP22: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP23: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP24: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP25: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP26: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP27: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP28: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP29: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP30: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP31: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP32: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP33: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP34: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP35: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP36: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP37: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP38: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP39: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP40: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP41: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP42: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP43: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP44: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP45: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP46: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP47: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP48: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP49: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))
    STEP50: Parameter[StringValue] = field(default_factory=lambda: Parameter(StringValue("")))

    @staticmethod
    def from_block(block: Block) -> CalcParameters:
        parameters = CalcParameters()

        for key, value in block.config.items():
            if len(value) == 0 or not hasattr(parameters, key) or key == "TYPE":
                continue

            p: Parameter = getattr(parameters, key)

            if "." not in value or ":" not in value:
                match p.get_value().get():
                    case int() | float():
                        p.get_value().set(float(value))
                    case bool():
                        p.get_value().set(bool(value))
                    case _:
                        p.get_value().set(value)
            elif match := CONNECTION_RE.match(value):
                setattr(
                    parameters,
                    key,
                    Parameter(
                        UnparsedConnection(
                            compound=match.group("compound") or block.compound,
                            block=match.group("block"),
                            parameter=match.group("parameter"),
                        ),
                    ),
                )

        return parameters

    def get_step(self, step_number: int) -> Input[StringValue]:
        return getattr(self, f"STEP{step_number:02d}")
