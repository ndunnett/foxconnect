from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .parameters import CalcParameters


@dataclass(frozen=True)
class NamedOperand:
    """Represents a named operand, addressed to a Calc block parameter."""

    prefix: str
    suffix: str
    inverted: bool

    def __str__(self) -> str:
        return "~" + self.name if self.inverted else self.name

    @staticmethod
    def parse(s: str) -> NamedOperand | None:
        if s.startswith("~"):
            inverted = True
            s = s[1:]
        else:
            inverted = False

        try:
            prefix = ""

            while s[0].isalpha():
                prefix += s[0]
                s = s[1:]

            return NamedOperand(prefix, s, inverted)

        except IndexError:
            return None

    @property
    def name(self) -> str:
        return f"{self.prefix}{self.suffix}"


Operand = NamedOperand | int
Operands = tuple[Operand, ...]
Operation = Callable[..., None]
Verifier = Callable[[Operands], bool]
Production = Callable[[], None]


def parse_operand(s: str) -> Operand | None:
    """Parse a string into an operand."""
    try:
        return int(s)
    except ValueError:
        return NamedOperand.parse(s)


def any_of(*verifiers: Verifier) -> Verifier:
    """Combine verifiers to return true when any verifier is satisfied."""
    return lambda operands: any(verifier(operands) for verifier in verifiers)


def all_of(*verifiers: Verifier) -> Verifier:
    """Combine verifiers to return true when all verifiers are satisfied."""
    return lambda operands: all(verifier(operands) for verifier in verifiers)


def no_operand(operands: Operands) -> bool:
    """Verify that no operands are given."""
    return len(operands) == 0


def one_operand(operands: Operands) -> bool:
    """Verify that one operand is given."""
    return len(operands) == 1


def named_operand(operands: Operands, prefix_rule: Callable[[str], bool]) -> bool:
    """Verify that a valid named operand is given."""
    return (
        len(operands) == 1
        and isinstance(operands[0], NamedOperand)
        and operands[0].name in CalcParameters.__dataclass_fields__
        and prefix_rule(operands[0].prefix)
    )


def const_operand(operands: Operands) -> bool:
    """Verify that the operand is a constant value."""
    return len(operands) == 1 and isinstance(operands[0], int)


def real(operands: Operands) -> bool:
    """Verify that the operand is a named real parameter."""
    return named_operand(operands, lambda prefix: prefix.startswith("R"))


def boolean(operands: Operands) -> bool:
    """Verify that the operand is a named boolean parameter."""
    return named_operand(operands, lambda prefix: prefix.startswith("B"))


def integer(operands: Operands) -> bool:
    """Verify that the operand is a named integer parameter."""
    return named_operand(operands, lambda prefix: prefix.startswith("I"))


def long(operands: Operands) -> bool:
    """Verify that the operand is a named long parameter."""
    return named_operand(operands, lambda prefix: prefix.startswith("L"))


def memory(operands: Operands) -> bool:
    """Verify that the operand is a named memory parameter."""
    return named_operand(operands, lambda prefix: prefix == "M")


def input_parameter(operands: Operands) -> bool:
    """Verify that the operand is a named input parameter."""
    return named_operand(operands, lambda prefix: prefix.endswith("I"))


def output_parameter(operands: Operands) -> bool:
    """Verify that the operand is a named output parameter."""
    return named_operand(operands, lambda prefix: prefix.endswith("O"))


def not_inverted(operands: Operands) -> bool:
    """Verify that the operand is not inverted."""
    return not (len(operands) == 1 and isinstance(operands[0], NamedOperand) and operands[0].inverted)
