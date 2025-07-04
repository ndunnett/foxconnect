from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from utils import clamp

from foxemu.blocks import EmulatedBlock
from foxemu.signaling import BoolValue, IntegerValue, LongValue, Parameter, RealValue

from .constants import INITIAL_SEED, MAX_STACK_LENGTH
from .errors import CalcError
from .operands import NamedOperand, Operands, parse_operand
from .parameters import CalcParameters

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from foxdata.models import Block


@dataclass
class StackElement:
    value: RealValue
    step: int


@dataclass
class Step:
    opcode: str
    operands: Operands


class Calc(EmulatedBlock):
    """Emulates CALC block type."""

    parameters: CalcParameters
    errors: list[tuple[int, CalcError]]
    stack: list[StackElement]
    program: list[Callable[[], None] | None]
    steps: dict[int, Step]
    pointer: int
    should_increment: bool
    should_terminate: bool
    syntax_error: bool
    seed: int

    def __init__(self, compound: str, name: str, parameters: CalcParameters) -> None:
        # Initialise parameters and persistent internal state
        super().__init__(compound, name)
        self.seed = INITIAL_SEED
        self.parameters = parameters
        self.parameters.MA.get_value().set(self.parameters.INITMA.get_value().get() != 0)

        # Initialise internal state that is reset upon execution
        self.errors = []
        self.stack = []
        self.pointer = 1
        self.should_increment = True
        self.should_terminate = False
        self.syntax_error = False

        # Parse steps into program, ie. list of productions to execute
        self.program = []
        self.steps = {}

        for i in range(1, 51):
            parameter = self.parameters.get_step(i)

            match self.parse_step(parameter.get_value().get()):
                case None:
                    self.program.append(None)
                case CalcError() as error:
                    self.program.append(None)
                    self.error(i, error)
                case (production, opcode, operands):
                    self.program.append(production)
                    self.steps[i] = Step(opcode, operands)

    @staticmethod
    def from_block(block: Block) -> Calc:
        """Create an emulated Calc block from a block model."""
        return Calc(block.compound, block.name, CalcParameters.from_block(block))

    def parameters_iter(self) -> Generator[Parameter]:
        """Iterate over block parameters."""
        return (
            attr
            for attr in filter(
                lambda attr: isinstance(attr, Parameter),
                self.parameters.__dict__.values(),
            )
        )

    def get_parameter(self, key: str) -> Parameter | None:
        """Get block parameter by name."""
        return getattr(self.parameters, key, None)

    def get_operand(self, operand: NamedOperand) -> float:
        """Get value of named operand."""
        p: Parameter[RealValue | IntegerValue | LongValue | BoolValue] | None = getattr(
            self.parameters,
            operand.name,
            None,
        )

        if p is None:
            self.error(self.pointer, CalcError.INVALID_OPERAND)
            return 0
        elif operand.inverted:
            return 1 if p.get_value().get() == 0 else 0
        elif operand.prefix[0] == "R":
            high = NamedOperand("HSC" + operand.prefix[1], operand.suffix[1], operand.inverted)
            low = NamedOperand("LSC" + operand.prefix[1], operand.suffix[1], operand.inverted)
            return float(clamp(p.get_value().get(), self.get_operand(low), self.get_operand(high)))
        else:
            return float(p.get_value().get())

    def set_operand(self, operand: NamedOperand, value: float | bool) -> None:  # noqa: FBT001
        """Set value of named operand."""
        p: Parameter[RealValue | IntegerValue | LongValue | BoolValue] | None = getattr(
            self.parameters,
            operand.name,
            None,
        )

        if p is None:
            self.error(self.pointer, CalcError.INVALID_OPERAND)
            return
        elif operand.prefix.startswith("M"):
            p.assign_value(RealValue(value))
        elif self.parameters.MA.get_value():
            match operand.prefix[0]:
                case "R":
                    high = NamedOperand("HSC" + operand.prefix[1], operand.suffix[1], operand.inverted)
                    low = NamedOperand("LSC" + operand.prefix[1], operand.suffix[1], operand.inverted)
                    p.assign_value(RealValue(clamp(value, self.get_operand(low), self.get_operand(high))))
                case "I":
                    p.assign_value(IntegerValue(value))
                case "L":
                    p.assign_value(LongValue(value))
                case "B":
                    p.assign_value(BoolValue(bool(value)))

    def parse_step(self, step: str) -> tuple[Callable[[], None], str, Operands] | None | CalcError:
        """Parse a string into a production with metadata."""
        # Empty string returns a no-op
        if len(step) == 0:
            return None

        from . import operations  # noqa: PLC0415

        # Strip comments and split into tokens
        tokens = re.sub(";.*", "", step).strip().split()

        match len(tokens):
            case 0:
                # No tokens, return no-op
                return None
            case 1:
                # Opcode without any operands
                opcode = tokens[0]
                operands = ()
            case _:
                # Opcode with operands, parse operands into a tuple
                opcode = tokens[0]
                operands = tuple(operand for s in tokens[1:] if (operand := parse_operand(s)) is not None)

        # Attempt to get producer from operations module
        producer: operations.Producer | None = getattr(operations, opcode, None)

        if producer is None:
            # Producer not found, opcode must be invalid
            return CalcError.INVALID_OPCODE
        elif production := producer(self, operands):
            # Producer found and operands verified, return production
            return (production, opcode, operands)
        else:
            # Producer found but operands failed verification
            return CalcError.INVALID_OPERAND

    def error(self, step_number: int, error: CalcError) -> None:
        """Set error parameters and append to errors list."""
        self.parameters.PERROR.get_value().set(error.value)
        self.parameters.STERR.get_value().set(step_number)
        self.errors.append((step_number, error))

        # Negative codes indicate syntax error rather than runtime error
        if error.value < 0:
            self.syntax_error = True

    def push(self, value: float) -> None:
        """Push value to the top of the stack."""
        self.stack.append(StackElement(value=RealValue(value), step=self.pointer))

        if len(self.stack) > MAX_STACK_LENGTH:
            self.stack.pop(0)
            self.error(self.pointer, CalcError.STACK_OVERFLOW)

    def pop(self) -> float:
        """Pop value from the top of the stack."""
        if not self.stack:
            self.error(self.pointer, CalcError.STACK_UNDERFLOW)
            return 0

        return self.stack.pop().value.get()

    def pop_many(self, n: int) -> list[float]:
        """Pop multiple values from the top of the stack."""
        # TODO: test behaviour on real system when n < 2  # noqa: FIX002
        return [self.pop() for _ in range(max(n, 0))]

    def pop_all(self) -> list[float]:
        """Pop all values from the stack."""
        values = [element.value.get() for element in self.stack]
        self.clear()
        return values

    def clear(self) -> None:
        """Clear all values from the stack."""
        self.stack.clear()

    def acc(self) -> float:
        """Return accumulator value (top of stack)."""
        return self.stack[-1].value.get()

    def jump(self, x: int) -> None:
        """Jump to step 'x'."""
        # Raise error if step number is invalid
        if x > len(self.program):
            self.error(self.pointer, CalcError.INVALID_GOTO)
            return

        # Set pointer to desired step and skip next pointer increment
        self.pointer = x
        self.should_increment = False

    def rng(self) -> float:
        """Generate pseudo-random real value of uniform distrubtion in range [0,1]."""
        self.seed = self.seed * 125 % 2796203
        return RealValue(self.seed / 2796203).get()

    def execute(self) -> None:
        """Execute the block once."""
        # Shouldn't execute if there is a syntax error
        if self.syntax_error:
            return

        # Reset internal state
        self.errors = []
        self.stack = []
        self.pointer = 1
        self.should_increment = True
        self.should_terminate = False

        # Execute program for a full cycle
        while not self.should_terminate and self.pointer <= len(self.program):
            if operation := self.program[self.pointer - 1]:
                operation()

            if self.should_increment:
                self.pointer += 1
            else:
                self.should_increment = True

    def generate_dot(self) -> str:
        from .graphing import generate_dot  # noqa: PLC0415

        return generate_dot(self)
