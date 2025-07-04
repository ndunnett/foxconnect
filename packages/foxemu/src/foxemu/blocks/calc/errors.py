from enum import Enum, auto


class CalcError(Enum):
    INVALID_GOTO = -4
    OPERAND_OOR = -3
    INVALID_OPERAND = -2
    INVALID_OPCODE = -1
    NO_ERROR = 0
    SQRT = 1
    ASIN = 2
    ACOS = 3
    DIV = 4
    STACK_OVERFLOW = 5
    STACK_UNDERFLOW = 6
    LOG = 7
    LN = 8
    EXP = 9
    INDEX = 10
    BIT = 11

    def __str__(self) -> str:
        return f"{self.description} (code {self.value})"

    @property
    def description(self) -> str:
        return CALC_ERROR_DESCRIPTIONS[self]


CALC_ERROR_DESCRIPTIONS = {
    CalcError.INVALID_GOTO: "invalid go to step number",
    CalcError.OPERAND_OOR: "out of range operand index",
    CalcError.INVALID_OPERAND: "invalid operand type",
    CalcError.INVALID_OPCODE: "invalid operation code",
    CalcError.NO_ERROR: "no error",
    CalcError.SQRT: "SQRT error (accumulator < 0)",
    CalcError.ASIN: "ASIN error (absolute value of accumulator > 1)",
    CalcError.ACOS: "ACOS error (absolute value of accumulator > 1)",
    CalcError.DIV: "DIV error (divide by zero)",
    CalcError.STACK_OVERFLOW: "stack overflow",
    CalcError.STACK_UNDERFLOW: "stack underflow",
    CalcError.LOG: "LOG error (accumulator <= 0)",
    CalcError.LN: "LN error (accumulator <= 0)",
    CalcError.EXP: "EXP error (base < 0)",
    CalcError.INDEX: "index error",
    CalcError.BIT: "bit error",
}


class GraphingError(Enum):
    BREAKING_INSTRUCTION = auto()
    INVALID_OPERAND = auto()

    def __str__(self) -> str:
        return f"{self.description}"

    @property
    def description(self) -> str:
        return GRAPHING_ERROR_DESCRIPTIONS[self]


GRAPHING_ERROR_DESCRIPTIONS = {
    GraphingError.BREAKING_INSTRUCTION: "graphing not possible for opcode",
    GraphingError.INVALID_OPERAND: "invalid operand makes graphing impossible",
}
