# ruff: noqa: FIX002, N802, D401, D415

import math
from collections.abc import Callable
from functools import reduce

from foxemu.signaling import IntegerValue, Parameter

from .block import Calc
from .constants import INITIAL_SEED
from .errors import CalcError
from .operands import (
    NamedOperand,
    Operands,
    Operation,
    Production,
    Verifier,
    all_of,
    any_of,
    boolean,
    const_operand,
    input_parameter,
    integer,
    long,
    memory,
    no_operand,
    not_inverted,
    output_parameter,
    real,
)

Producer = Callable[[Calc, Operands], Production | None]


def verify(func: Verifier) -> Callable[[Operation], Producer]:
    """
    Decorate Operations to transform them into Producers.

    Transforms the function to verify operands and return another function to produce the executable step.
    Use a combination of verification functions to apply rules for what operands an operation can accept.

    e.g.

    `@verify(any_of(no_operand, const_operand))` - either no operand or a single constant operand is acceptable.

    `@verify(all_of(real, not_inverted))` - operand is required, must be a real, and must not be inverted.
    """

    def decorator(operation: Operation) -> Producer:
        def producer(block: Calc, operands: Operands) -> Production | None:
            named_operands_exist = all(
                hasattr(block.parameters, operand.name) for operand in operands if isinstance(operand, NamedOperand)
            )

            if named_operands_exist and func(operands):
                return lambda: operation(block, *operands)
            else:
                return None

        return producer

    return decorator


@verify(no_operand)
def ABS(block: Calc) -> None:
    """Absolute Value (Unary)"""
    block.push(abs(block.pop()))


@verify(no_operand)
def ACOS(block: Calc) -> None:
    """Arc Cosine (Unary)"""
    x = block.pop()
    if x > 1 or x < -1:
        block.error(block.pointer, CalcError.ACOS)
        block.push(x)
    else:
        block.push(math.acos(x))


@verify(any_of(no_operand, const_operand, all_of(any_of(real, memory), not_inverted)))
def ADD(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Add (Diadic or Polyadic)"""
    if operand is None:
        block.push(sum(block.pop_many(2)))
    elif isinstance(operand, int):
        block.push(sum(block.pop_many(operand)))
    else:
        block.push(block.pop() + block.get_operand(operand))


@verify(no_operand)
def ALN(block: Calc) -> None:
    """Natural Antilog (Unary)"""
    block.push(math.exp(block.pop()))


@verify(no_operand)
def ALOG(block: Calc) -> None:
    """Common Antilog (Unary)"""
    block.push(10 ** block.pop())


@verify(any_of(no_operand, const_operand, boolean, integer, memory))
def AND(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Logical And (Diadic or Polyadic)"""
    # TODO: verify meaning of "Ixx" and "Oxx" operands on real system

    if operand is None:
        operands = [int(value) for value in block.pop_all()]
    elif isinstance(operand, int):
        operands = [int(operand) for operand in block.pop_many(operand)]
    else:
        operands = [int(block.pop()), int(block.get_operand(operand))]

    block.push(1 if all(operand != 0 for operand in operands) else 0)


@verify(any_of(no_operand, const_operand))
def ANDX(block: Calc, operand: int | None = None) -> None:
    """Packed Logical And (Polyadic)"""
    # TODO: implement and test ANDX
    pass


@verify(no_operand)
def ASIN(block: Calc) -> None:
    """Arc Sine (Unary)"""
    x = block.pop()
    if x > 1 or x < -1:
        block.error(block.pointer, CalcError.ASIN)
        block.push(x)
    else:
        block.push(math.asin(x))


@verify(no_operand)
def ATAN(block: Calc) -> None:
    """Arc Tangent (Unary)"""
    block.push(math.atan(block.pop()))


@verify(any_of(no_operand, const_operand, all_of(any_of(real, memory), not_inverted)))
def AVE(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Average (Diadic or Polyadic)"""
    if operand is None:
        operands = block.pop_many(2)
        block.push(sum(operands) / len(operands))
    elif isinstance(operand, int):
        operands = block.pop_many(operand)
        block.push(sum(operands) / len(operands))
    else:
        block.push((block.pop() + block.get_operand(operand)) / 2)


@verify(const_operand)
def BII(block: Calc, operand: int) -> None:
    """Branch If Initializing (Conditional Branch)"""
    # TODO: implement and test BII
    pass


@verify(const_operand)
def BIN(block: Calc, operand: int) -> None:
    """Branch If Negative (Conditional Branch)"""
    if block.acc() < 0:
        block.jump(operand)


@verify(const_operand)
def BIP(block: Calc, operand: int) -> None:
    """Branch If Positive or Zero (Conditional Branch)"""
    if block.acc() >= 0:
        block.jump(operand)


@verify(const_operand)
def BIT(block: Calc, operand: int) -> None:
    """Branch If True (Conditional Branch)"""
    if block.acc() != 0:
        block.jump(operand)


@verify(const_operand)
def BIZ(block: Calc, operand: int) -> None:
    """Branch If Zero (Conditional Branch)"""
    if block.acc() == 0:
        block.jump(operand)


BIF = BIZ
"""Branch If False (Conditional Branch)"""


@verify(all_of(output_parameter, not_inverted))
def CBD(block: Calc, operand: NamedOperand) -> None:
    """Clear Bad Status (Output Status)"""
    # TODO: implement and test CBD
    pass


@verify(all_of(output_parameter, not_inverted))
def CE(block: Calc, operand: NamedOperand) -> None:
    """Clear Error Status (Output Status)"""
    # TODO: implement and test CE
    pass


@verify(no_operand)
def CHI(block: Calc) -> None:
    """Clear History"""
    # TODO: implement and test CHI
    pass


@verify(const_operand)
def CHN(block: Calc, operand: int) -> None:
    """Clear Step History"""
    # TODO: implement and test CHN
    pass


@verify(no_operand)
def CHS(block: Calc) -> None:
    """Change Sign (Unary)"""
    block.push(-block.pop())


@verify(no_operand)
def CLA(block: Calc) -> None:
    """Clear All Memory Registers (Memory)"""
    for x in range(1, 25):
        p: Parameter = getattr(block.parameters, f"M{x:02d}")
        p.get_value().set(0)


@verify(no_operand)
def CLE(block: Calc) -> None:
    """Clear Error Flag Error Control"""
    # TODO: implement and test CLE
    pass


@verify(all_of(memory, not_inverted))
def CLM(block: Calc, operand: NamedOperand) -> None:
    """Clear Memory Register (Memory)"""
    # TODO: test CLM
    block.set_operand(operand, 0)


@verify(any_of(no_operand, all_of(any_of(output_parameter, memory), not_inverted)))
def CLR(block: Calc, operand: NamedOperand | None = None) -> None:
    """Clear (Unconditional Clear)"""
    # TODO: implement and test CLR
    pass


@verify(any_of(no_operand, const_operand))
def CLRB(block: Calc, operand: int | None = None) -> None:
    """Clear Packed Boolean (Unconditional Clear)"""
    # TODO: implement and test CLRB
    pass


@verify(all_of(output_parameter, not_inverted))
def COO(block: Calc, operand: NamedOperand) -> None:
    """Clear Out-of-Service Status (Output Status)"""
    # TODO: implement and test COO
    pass


@verify(no_operand)
def COS(block: Calc) -> None:
    """Cosine (Unary)"""
    block.push(math.cos(block.pop()))


@verify(no_operand)
def CST(block: Calc) -> None:
    """Clear Stack (Stack)"""
    # TODO: test CST
    block.clear()


@verify(
    any_of(
        no_operand,
        const_operand,
        all_of(any_of(all_of(any_of(real, integer, long), output_parameter), memory), not_inverted),
    ),
)
def DEC(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Decrement (Unary)"""
    if operand is None:
        block.push(max(-16_777_215, block.pop() - 1))
    elif isinstance(operand, int):
        block.push(max(-16_777_215, block.pop() - operand))
    else:
        block.set_operand(operand, block.get_operand(operand) - 1)


@verify(any_of(no_operand, all_of(any_of(real, memory), not_inverted)))
def DIV(block: Calc, operand: NamedOperand | None = None) -> None:
    """Divide (Diadic)"""
    if operand is None:
        denominator = block.pop()
        numerator = block.pop()
    else:
        denominator = block.get_operand(operand)
        numerator = block.pop()

    if denominator == 0:
        block.error(block.pointer, CalcError.DIV)
        block.push(0)
    else:
        block.push(numerator / denominator)


@verify(any_of(no_operand, const_operand, all_of(memory, not_inverted)))
def DOFF(block: Calc, operand: NamedOperand) -> None:
    """Delayed OFF Timing"""
    # TODO: implement and test DOFF
    pass


@verify(any_of(no_operand, const_operand, all_of(memory, not_inverted)))
def DON(block: Calc, operand: NamedOperand) -> None:
    """Delayed ON Timing"""
    # TODO: implement and test DON
    pass


@verify(no_operand)
def DUP(block: Calc) -> None:
    """Duplicate (Stack)"""
    # TODO: implement and test DUP
    pass


@verify(no_operand)
def END(block: Calc) -> None:
    """End Program (Program Termination)"""
    block.should_terminate = True


@verify(no_operand)
def EXIT(block: Calc) -> None:
    """Exit Program (Program Termination)"""
    block.should_terminate = True


@verify(any_of(no_operand, all_of(any_of(real, memory), not_inverted)))
def EXP(block: Calc, operand: NamedOperand | None = None) -> None:
    """Exponent (Diadic)"""
    if operand is None:
        exponent = block.pop()
        base = block.pop()
    else:
        exponent = block.get_operand(operand)
        base = block.pop()

    if base < 0:
        block.push(exponent)
        block.error(block.pointer, CalcError.EXP)
    elif base == 0 and exponent <= 0:
        block.push(0)
    else:
        block.push(base**exponent)


@verify(no_operand)
def FF(block: Calc) -> None:
    """Flip-Flop (Logic)"""
    # TODO: test FF
    reset_value = bool(block.pop())
    set_value = bool(block.pop())

    match (set_value, reset_value):
        case (False, False):
            block.push(block.acc())
        case (False, True):
            block.push(0)
        case (True, False):
            block.push(1)
        case (True, True):
            block.push(block.acc())


@verify(all_of(any_of(real, integer, memory), not_inverted))
def GTI(block: Calc, operand: NamedOperand) -> None:
    """Go To Indirect (Unconditional Branch)"""
    # TODO: implement and test GTI
    pass


@verify(const_operand)
def GTO(block: Calc, operand: int) -> None:
    """Go To (Unconditional Branch)"""
    block.jump(operand)


@verify(any_of(no_operand, all_of(memory, not_inverted)))
def IDIV(block: Calc, operand: NamedOperand | None = None) -> None:
    """Integer Division (Diadic)"""
    denominator = IntegerValue(block.pop()).get()
    numerator = IntegerValue(block.pop()).get()

    if denominator == 0:
        block.error(block.pointer, CalcError.DIV)
        block.push(0)

    quotient = numerator // denominator
    remainder = numerator - quotient * denominator

    block.push(quotient)

    if operand is not None:
        block.set_operand(operand, remainder)


@verify(no_operand)
def IMOD(block: Calc) -> None:
    """Integer Modulus (Diadic)"""
    denominator = IntegerValue(block.pop()).get()
    numerator = IntegerValue(block.pop()).get()

    if denominator == 0:
        block.error(block.pointer, CalcError.DIV)
        block.push(0)

    block.push(numerator % denominator)


@verify(any_of(no_operand, const_operand, real, integer, boolean, memory))
def IN(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Input (Input Value)"""
    if operand is None:
        block.push(0)
    elif isinstance(operand, int):
        block.push(operand)
    else:
        block.push(block.get_operand(operand))


@verify(any_of(no_operand, all_of(any_of(all_of(integer, input_parameter), memory), not_inverted)))
def INB(block: Calc, operand: NamedOperand | None = None) -> None:
    """Input Indexed Boolean (Input Value)"""
    # TODO: implement and test INB
    pass


@verify(
    any_of(
        no_operand,
        const_operand,
        all_of(any_of(all_of(any_of(real, integer, long), output_parameter), memory), not_inverted),
    ),
)
def INC(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Increment (Unary)"""
    if operand is None:
        block.push(min(16_777_214, block.pop() + 1))
    elif isinstance(operand, int):
        block.push(min(16_777_214, block.pop() + operand))
    else:
        block.set_operand(operand, block.get_operand(operand) + 1)


@verify(all_of(long, not_inverted))
def INH(block: Calc, operand: NamedOperand) -> None:
    """Input High Order (Input Value)"""
    # TODO: implement and test INH
    pass


@verify(all_of(long, not_inverted))
def INL(block: Calc, operand: NamedOperand) -> None:
    """Input Low Order (Input Value)"""
    # TODO: implement and test INL
    pass


@verify(any_of(no_operand, all_of(any_of(all_of(integer, output_parameter), memory), not_inverted)))
def INR(block: Calc, operand: NamedOperand | None = None) -> None:
    """Input Indexed Real (Input Value)"""
    # TODO: implement and test INR
    pass


@verify(all_of(any_of(real, boolean, integer, long), not_inverted))
def INS(block: Calc, operand: NamedOperand) -> None:
    """Input Status (Input Status)"""
    # TODO: implement and test INS
    pass


@verify(all_of(memory, not_inverted))
def LAC(block: Calc, operand: NamedOperand) -> None:
    """Load Accumulator (Memory/Stack)"""
    # TODO: implement and test LAC
    pass


@verify(all_of(memory, not_inverted))
def LACI(block: Calc, operand: NamedOperand) -> None:
    """Load Accumulator Indirect (Memory/Stack)"""
    # TODO: implement and test LACI
    pass


@verify(no_operand)
def LN(block: Calc) -> None:
    """Natural Logarithm (Unary)"""
    if block.acc() <= 0:
        block.error(block.pointer, CalcError.LN)
    else:
        block.push(math.log(block.pop()))


@verify(no_operand)
def LOG(block: Calc) -> None:
    """Common Logarithm (Unary)"""
    if block.acc() <= 0:
        block.error(block.pointer, CalcError.LOG)
    else:
        block.push(math.log10(block.pop()))


@verify(any_of(no_operand, const_operand, all_of(any_of(real, memory), not_inverted)))
def MAX(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Maximum (Diadic or Polyadic)"""
    if operand is None:
        block.push(max(block.pop_all()))
    elif isinstance(operand, int):
        block.push(max(block.pop_many(operand)))
    else:
        block.push(max(block.pop(), block.get_operand(operand)))


MAXO = MAX
"""Identical to MAX"""


@verify(no_operand)
def MEDN(block: Calc) -> None:
    """Median (Polyadic)"""
    if stack_values := sorted(block.pop_all()):
        mid = len(stack_values) / 2

        if mid % 1 == 0:
            block.push((stack_values[int(mid - 1)] + stack_values[int(mid)]) / 2)
        else:
            block.push(stack_values[int(mid)])
    else:
        block.push(0)


@verify(any_of(no_operand, const_operand, all_of(any_of(real, memory), not_inverted)))
def MIN(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Minimum (Diadic or Polyadic)"""
    if operand is None:
        block.push(min(block.pop_all()))
    elif isinstance(operand, int):
        block.push(min(block.pop_many(operand)))
    else:
        block.push(min(block.pop(), block.get_operand(operand)))


@verify(no_operand)
def MRS(block: Calc) -> None:
    """Master Reset Flip-Flop (Logic)"""
    # TODO: test MRS
    reset_value = bool(block.pop())
    set_value = bool(block.pop())

    match (set_value, reset_value):
        case (False, False):
            block.push(block.acc())
        case (False, True):
            block.push(0)
        case (True, False):
            block.push(1)
        case (True, True):
            block.push(0)


@verify(any_of(no_operand, const_operand, all_of(any_of(real, memory), not_inverted)))
def MUL(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Multiply (Diadic or Polyadic)"""
    if operand is None:
        block.push(block.pop() * block.pop())
    elif isinstance(operand, int):
        block.push(reduce(lambda a, b: a * b, block.pop_many(operand)))
    else:
        block.push(block.pop() * block.get_operand(operand))


@verify(any_of(no_operand, const_operand, real, integer, boolean))
def NAND(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Logical Not And (Diadic or Polyadic)"""
    # TODO: implement and test NAND
    pass


@verify(any_of(no_operand, const_operand))
def NANX(block: Calc, operand: int | None = None) -> None:
    """Packed Logical NAND (Polyadic)"""
    # TODO: implement and test NANX
    pass


@verify(no_operand)
def NOP(_: Calc) -> None:
    """No Operation (Unconditional Branch)"""
    return


@verify(any_of(no_operand, const_operand, real, integer, boolean))
def NOR(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Logical Not Or (Diadic or Polyadic)"""
    # TODO: test NOR
    if operand is None:
        values = [int(value) != 0 for value in block.pop_all()]
    elif isinstance(operand, int):
        values = [int(value) != 0 for value in block.pop_many(operand)]
    else:
        values = [int(block.pop()) != 0, int(block.get_operand(operand)) != 0]

    block.push(0 if any(values) else 1)


@verify(any_of(no_operand, const_operand))
def NORX(block: Calc, operand: int | None = None) -> None:
    """Packed Logical Nor Or (Polyadic. Packed Boolean)"""
    # TODO: implement and test NORX
    pass


@verify(no_operand)
def NOT(block: Calc) -> None:
    """Not (Unary)"""
    # TODO: implement and test NOT
    pass


@verify(no_operand)
def NOTX(block: Calc) -> None:
    """Packed Logical Not (Unary, Packed Boolean)"""
    # TODO: implement and test NOTX
    pass


@verify(any_of(no_operand, const_operand, real, integer, boolean))
def NXOR(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Logical Not Exclusive Or (Diadic or Polyadic, Packed Boolean)"""
    # TODO: implement and test NXOR
    pass


@verify(any_of(no_operand, const_operand))
def NXOX(block: Calc, operand: int | None = None) -> None:
    """Packed Logical Not Exclusive Or (Polyadic, Packed Boolean)"""
    # TODO: implement and test NXOX
    pass


@verify(any_of(no_operand, const_operand, real, integer, boolean))
def OR(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Logical Or (Diadic or Polyadic)"""
    if operand is None:
        values = [int(value) != 0 for value in block.pop_all()]
    elif isinstance(operand, int):
        values = [int(value) != 0 for value in block.pop_many(operand)]
    else:
        values = [int(block.pop()) != 0, int(block.get_operand(operand)) != 0]

    block.push(1 if any(values) else 0)


@verify(any_of(no_operand, const_operand))
def ORX(block: Calc, operand: int | None = None) -> None:
    """Packed Logical Or (Polyadic, Packed Boolean)"""
    # TODO: implement and test ORX
    pass


@verify(all_of(memory, not_inverted))
def OSP(block: Calc, operand: NamedOperand) -> None:
    """One-Shot Pulse Timing"""
    # TODO: implement and test OSP
    pass


@verify(any_of(all_of(output_parameter, not_inverted), all_of(boolean, output_parameter), memory))
def OUT(block: Calc, operand: NamedOperand) -> None:
    """Output (Output Value)"""
    block.set_operand(operand, block.acc())


@verify(no_operand)
def POP(block: Calc) -> None:
    """Pop Stack (Stack)"""
    block.pop()


@verify(all_of(real, output_parameter, not_inverted))
def PRI(block: Calc, operand: NamedOperand) -> None:
    """Propagate Upstream (Cascade/Propagation)"""
    # TODO: implement and test PRI
    pass


@verify(all_of(real, output_parameter, not_inverted))
def PRO(block: Calc, operand: NamedOperand) -> None:
    """Propagate Downstream (Cascade)"""
    # TODO: implement and test PRO
    pass


@verify(all_of(real, output_parameter, not_inverted))
def PRP(block: Calc, operand: NamedOperand) -> None:
    """Propagate Errors (Propagation)"""
    # TODO: implement and test PRP
    pass


@verify(no_operand)
def RAND(block: Calc) -> None:
    """Generate Random Number (Unary)"""
    block.push(block.rng())


@verify(no_operand)
def RANG(block: Calc) -> None:
    """Generate Random Number, Gaussian (Unary)"""
    block.push((-2 * math.log(block.rng())) ** 0.5 * math.cos(2 * math.pi * block.rng()))


@verify(all_of(any_of(real, boolean, integer, long), not_inverted))
def RBD(block: Calc, operand: NamedOperand) -> None:
    """Read Bad and OOS Bits (Input Status)"""
    # TODO: implement and test RBD
    pass


@verify(any_of(real, boolean, integer, long, memory))
def RCL(block: Calc, operand: NamedOperand) -> None:
    """Read and Clear (Input Value/Unconditional Clear)"""
    # TODO: test RCL
    block.push(block.get_operand(operand))
    block.set_operand(operand, 0)


@verify(all_of(any_of(real, integer, long, boolean), input_parameter, not_inverted))
def RCN(block: Calc, operand: NamedOperand) -> None:
    """Read Connect Status (Input Linkage Type)"""
    # TODO: implement and test RCN
    pass


@verify(all_of(any_of(real, integer, long, boolean), not_inverted))
def RE(block: Calc, operand: NamedOperand) -> None:
    """Read Error Bit (Input Status)"""
    # TODO: implement and test RE
    pass


@verify(all_of(any_of(real, integer, long, boolean), output_parameter, not_inverted))
def REL(block: Calc, operand: NamedOperand) -> None:
    """Clear Secure Status (Output Status)"""
    # TODO: implement and test REL
    pass


@verify(no_operand)
def RER(block: Calc) -> None:
    """Read Error Flag Error Control"""
    # TODO: implement and test RER
    pass


@verify(no_operand)
def RND(block: Calc) -> None:
    """Round (Unary)"""
    block.push(round(block.pop(), 0))


@verify(all_of(any_of(real, integer, long, boolean), not_inverted))
def RON(block: Calc, operand: NamedOperand) -> None:
    """Read In-Service Status (Input Status)"""
    # TODO: implement and test RON
    pass


@verify(all_of(any_of(real, integer, long, boolean), not_inverted))
def ROO(block: Calc, operand: NamedOperand) -> None:
    """Read OOS Bit (Input Status)"""
    # TODO: implement and test ROO
    pass


@verify(all_of(any_of(real, integer, long, boolean), input_parameter, not_inverted))
def RQE(block: Calc, operand: NamedOperand) -> None:
    """Read Quality Including Error (Input Status)"""
    # TODO: implement and test RQE
    pass


@verify(all_of(any_of(real, integer, long, boolean), input_parameter, not_inverted))
def RQL(block: Calc, operand: NamedOperand) -> None:
    """Read Quality (Input Status)"""
    # TODO: implement and test RQL
    pass


@verify(
    any_of(all_of(any_of(real, integer), output_parameter, not_inverted), all_of(boolean, output_parameter), memory),
)
def SAC(block: Calc, operand: NamedOperand) -> None:
    """Store Accumulator in Output (Output Value)"""
    # TODO: implement and test SAC
    pass


@verify(all_of(output_parameter, not_inverted))
def SBD(block: Calc, operand: NamedOperand) -> None:
    """Set Bad Status (Output Status)"""
    # TODO: implement and test SBD
    pass


@verify(all_of(output_parameter, not_inverted))
def SE(block: Calc, operand: NamedOperand) -> None:
    """Set Error Status (Output Status)"""
    # TODO: implement and test SE
    pass


@verify(all_of(output_parameter, not_inverted))
def SEC(block: Calc, operand: NamedOperand) -> None:
    """Set Secure Status (Output Status)"""
    # TODO: implement and test SEC
    pass


@verify(no_operand)
def SEED(block: Calc) -> None:
    """Seed Random Number Generator (Unary)"""
    if block.acc() < 0 or block.acc() > INITIAL_SEED:
        return
    else:
        block.seed = int(block.acc())


@verify(any_of(no_operand, all_of(any_of(output_parameter, memory), not_inverted)))
def SET(block: Calc, operand: NamedOperand | None = None) -> None:
    """Set (Unconditional Set)"""
    # TODO: implement and test SET
    pass


@verify(any_of(no_operand, const_operand))
def SETB(block: Calc, operand: int | None = None) -> None:
    """Set Packed Boolean (Unconditional Set)"""
    # TODO: implement and test SETB
    pass


@verify(no_operand)
def SIEC(block: Calc) -> None:
    """Skip if Error Cleared Error Control"""
    # TODO: implement and test SIEC
    pass


@verify(no_operand)
def SIN(block: Calc) -> None:
    """Sine (Unary)"""
    block.push(math.sin(block.pop()))


@verify(all_of(output_parameter, not_inverted))
def SOO(block: Calc, operand: NamedOperand) -> None:
    """Set Out-of-Service Status (Output Status)"""
    # TODO: implement and test SOO
    pass


@verify(no_operand)
def SQR(block: Calc) -> None:
    """Square (Unary)"""
    block.push(block.pop() ** 2)


@verify(no_operand)
def SQRT(block: Calc) -> None:
    """Square Root (Unary)"""
    operand = block.pop()

    if operand < 0:
        block.error(block.pointer, CalcError.SQRT)
    else:
        block.push(math.sqrt(operand))


@verify(all_of(any_of(output_parameter, memory), not_inverted))
def SSI(block: Calc, operand: NamedOperand) -> None:
    """Set Boolean and Skip if Block Initializing (Program Control)"""
    # TODO: implement and test SSI
    pass


@verify(all_of(any_of(output_parameter, memory), not_inverted))
def SSN(block: Calc, operand: NamedOperand) -> None:
    """Set Boolean and Skip if Accumulator Negative (Program Control)"""
    # TODO: test SSN
    if block.acc() < 0:
        block.set_operand(operand, 1)
        block.pointer += 1


@verify(all_of(any_of(output_parameter, memory), not_inverted))
def SSP(block: Calc, operand: NamedOperand) -> None:
    """Set Boolean and Skip if Accumulator Positive (Program Control)"""
    # TODO: test SSP
    if block.acc() >= 0:
        block.set_operand(operand, 1)
        block.pointer += 1


@verify(all_of(any_of(output_parameter, memory), not_inverted))
def SST(block: Calc, operand: NamedOperand) -> None:
    """Set Boolean and Skip if Accumulator True (Program Control)"""
    # TODO: test SST
    if block.acc() != 0:
        block.set_operand(operand, 1)
        block.pointer += 1


@verify(all_of(any_of(output_parameter, memory), not_inverted))
def SSZ(block: Calc, operand: NamedOperand) -> None:
    """Set Boolean and Skip if Accumulator Zero (Program Control)"""
    # TODO: test SSZ
    if block.acc() == 0:
        block.set_operand(operand, 1)
        block.pointer += 1


SSF = SSZ
"""Set Boolean and Skip if Accumulator False (Program Control)"""


@verify(all_of(long, output_parameter, not_inverted))
def STH(block: Calc, operand: NamedOperand) -> None:
    """Store High Order (Output Value)"""
    # TODO: implement and test STH
    pass


@verify(all_of(long, output_parameter, not_inverted))
def STL(block: Calc, operand: NamedOperand) -> None:
    """Store Low Order (Output Value)"""
    # TODO: implement and test STL
    pass


@verify(all_of(memory, not_inverted))
def STM(block: Calc, operand: NamedOperand) -> None:
    """Store Memory (Memory/Stack)"""
    block.set_operand(operand, block.acc())


@verify(all_of(memory, not_inverted))
def STMI(block: Calc, operand: NamedOperand) -> None:
    """Store Memory Indirect (Memory/Stack)"""
    # TODO: implement and test STMI
    pass


@verify(any_of(no_operand, all_of(any_of(real, memory), not_inverted)))
def SUB(block: Calc, operand: NamedOperand | None = None) -> None:
    """Subtract (Diadic)"""
    if operand is None:
        block.push(-block.pop() + block.pop())
    else:
        block.push(block.pop() - block.get_operand(operand))


@verify(
    any_of(no_operand, all_of(any_of(all_of(any_of(real, boolean, integer), output_parameter), memory), not_inverted)),
)
def SWP(block: Calc, operand: NamedOperand | None = None) -> None:
    """Swap (Operand/Stack)"""
    # TODO: implement and test SWP
    pass


@verify(no_operand)
def TAN(block: Calc) -> None:
    """Tangent (Unary)"""
    block.push(math.tan(block.pop()))


@verify(no_operand)
def TIM(block: Calc) -> None:
    """Time Since Midnight Time Reporting"""
    # TODO: implement and test TIM
    pass


@verify(no_operand)
def TRC(block: Calc) -> None:
    """Truncate (Unary)"""
    operand = block.pop()
    block.push(operand - operand % 1)


@verify(any_of(no_operand, const_operand))
def TSTB(block: Calc, operand: int | None = None) -> None:
    """Test Packed Boolean (Stack)"""
    # TODO: implement and test TSTB
    pass


@verify(any_of(no_operand, const_operand, any_of(boolean, integer, memory)))
def XOR(block: Calc, operand: NamedOperand | int | None = None) -> None:
    """Logical Exclusive Or (Diadic or Polyadic)"""
    # TODO: implement and test XOR
    pass


@verify(any_of(no_operand, const_operand))
def XORX(block: Calc, operand: int | None = None) -> None:
    """Packed Logical Exclusive Or (Polyadic, Packed Boolean)"""
    # TODO: implement and test XORX
    pass
