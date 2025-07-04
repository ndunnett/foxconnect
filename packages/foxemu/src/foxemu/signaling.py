# ruff: noqa: ANN401
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
from utils import clamp

if TYPE_CHECKING:
    from foxemu.blocks import EmulatedBlock
    from foxemu.emulator import Emulator


class BaseValue[T]:
    """Base object for emulated values."""

    _value: T

    def __init__(self, value: T) -> None:
        self.set(value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._value})"

    def get(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        self._value = self.emulate_precision(value)

    def emulate_precision(self, value: T) -> T:
        return value


class RealValue(BaseValue[float]):
    def emulate_precision(self, value: float) -> float:
        return clamp(float(np.float16(value)), -pow(10, 38), pow(10, 38))

    def __abs__(self) -> RealValue:
        return RealValue(abs(self._value))

    def __add__(self, other: Any) -> RealValue:
        if issubclass(other, RealValue | IntegerValue):
            return RealValue(self._value + other._value)
        return RealValue(self._value + other)

    def __sub__(self, other: Any) -> RealValue:
        if issubclass(other, RealValue | IntegerValue):
            return RealValue(self._value - other._value)
        return RealValue(self._value - other)

    def __mul__(self, other: Any) -> RealValue:
        if issubclass(other, RealValue | IntegerValue):
            return RealValue(self._value * other._value)
        return RealValue(self._value * other)

    def __truediv__(self, other: Any) -> RealValue:
        if issubclass(other, RealValue | IntegerValue):
            return RealValue(self._value / other._value)
        return RealValue(self._value / other)


class IntegerValue(BaseValue[int]):
    def __init__(self, value: float) -> None:
        self.set(value)

    def set(self, value: float) -> None:
        self._value = self.emulate_precision(value)

    def emulate_precision(self, value: float) -> int:
        return int(clamp(value, -32768, 32767))

    def __abs__(self) -> IntegerValue:
        return IntegerValue(abs(self._value))

    def __add__(self, other: Any) -> IntegerValue:
        if issubclass(other, RealValue | IntegerValue):
            return IntegerValue(self._value + other._value)
        return IntegerValue(self._value + other)

    def __sub__(self, other: Any) -> IntegerValue:
        if issubclass(other, RealValue | IntegerValue):
            return IntegerValue(self._value - other._value)
        return IntegerValue(self._value - other)

    def __mul__(self, other: Any) -> IntegerValue:
        if issubclass(other, RealValue | IntegerValue):
            return IntegerValue(self._value * other._value)
        return IntegerValue(self._value * other)

    def __truediv__(self, other: Any) -> IntegerValue:
        if issubclass(other, RealValue | IntegerValue):
            return IntegerValue(self._value / other._value)
        return IntegerValue(self._value / other)


class ShortValue(IntegerValue):
    def emulate_precision(self, value: float) -> int:
        return int(clamp(value, -128, 127))

    def __abs__(self) -> ShortValue:
        return ShortValue(abs(self._value))

    def __add__(self, other: Any) -> ShortValue:
        if issubclass(other, RealValue | IntegerValue):
            return ShortValue(self._value + other._value)
        return ShortValue(self._value + other)

    def __sub__(self, other: Any) -> ShortValue:
        if issubclass(other, RealValue | IntegerValue):
            return ShortValue(self._value - other._value)
        return ShortValue(self._value - other)

    def __mul__(self, other: Any) -> ShortValue:
        if issubclass(other, RealValue | IntegerValue):
            return ShortValue(self._value * other._value)
        return ShortValue(self._value * other)

    def __truediv__(self, other: Any) -> ShortValue:
        if issubclass(other, RealValue | IntegerValue):
            return ShortValue(self._value / other._value)
        return ShortValue(self._value / other)


class LongValue(IntegerValue):
    def emulate_precision(self, value: float) -> int:
        return int(clamp(value, -2147483648, 2147483647))

    def __abs__(self) -> LongValue:
        return LongValue(abs(self._value))

    def __add__(self, other: Any) -> LongValue:
        if issubclass(other, RealValue | IntegerValue):
            return LongValue(self._value + other._value)
        return LongValue(self._value + other)

    def __sub__(self, other: Any) -> LongValue:
        if issubclass(other, RealValue | IntegerValue):
            return LongValue(self._value - other._value)
        return LongValue(self._value - other)

    def __mul__(self, other: Any) -> LongValue:
        if issubclass(other, RealValue | IntegerValue):
            return LongValue(self._value * other._value)
        return LongValue(self._value * other)

    def __truediv__(self, other: Any) -> LongValue:
        if issubclass(other, RealValue | IntegerValue):
            return LongValue(self._value / other._value)
        return LongValue(self._value / other)


class BoolValue(BaseValue[bool]): ...


class StringValue(BaseValue[str]): ...


Value = RealValue | IntegerValue | ShortValue | LongValue | BoolValue | StringValue


class Status(int):
    """Emulates signal status data as a packed integer."""

    # DATA_BIT = 0  # noqa: ERA001
    # DATA_BIT = 1  # noqa: ERA001
    # DATA_BIT = 2  # noqa: ERA001
    # DATA_BIT = 3  # noqa: ERA001
    # DATA_BIT = 4  # noqa: ERA001
    # OM_BIT = 5  # noqa: ERA001
    # OM_BIT = 6  # noqa: ERA001
    # OM_BIT = 7  # noqa: ERA001
    BAD_BIT = 8
    SECURE_RELEASE_BIT = 9
    ACK_BIT = 10
    OOS_BIT = 11
    SHADOW_BIT = 12
    LIM_HIGH_BIT = 13
    LIM_LOW_BIT = 14
    PROPAGATED_BIT = 15

    @staticmethod
    def _getter(status: int, bit: int) -> bool:
        return status & bit == 1

    @staticmethod
    def _setter(status: int, bit: int, *, value: bool) -> None:
        if value:
            status |= 1 << bit
        else:
            status &= ~(1 << bit)

    @property
    def bad(self) -> bool:
        return Status._getter(self, Status.BAD_BIT)

    @bad.setter
    def bad(self, value: bool) -> None:
        Status._setter(self, Status.BAD_BIT, value=value)

    @property
    def secure_release(self) -> bool:
        return Status._getter(self, Status.SECURE_RELEASE_BIT)

    @secure_release.setter
    def secure_release(self, value: bool) -> None:
        Status._setter(self, Status.SECURE_RELEASE_BIT, value=value)

    @property
    def ack(self) -> bool:
        return Status._getter(self, Status.ACK_BIT)

    @ack.setter
    def ack(self, value: bool) -> None:
        Status._setter(self, Status.ACK_BIT, value=value)

    @property
    def oos(self) -> bool:
        return Status._getter(self, Status.OOS_BIT)

    @oos.setter
    def oos(self, value: bool) -> None:
        Status._setter(self, Status.OOS_BIT, value=value)

    @property
    def shadow(self) -> bool:
        return Status._getter(self, Status.SHADOW_BIT)

    @shadow.setter
    def shadow(self, value: bool) -> None:
        Status._setter(self, Status.SHADOW_BIT, value=value)

    @property
    def lim_high(self) -> bool:
        return Status._getter(self, Status.LIM_HIGH_BIT)

    @lim_high.setter
    def lim_high(self, value: bool) -> None:
        Status._setter(self, Status.LIM_HIGH_BIT, value=value)

    @property
    def lim_low(self) -> bool:
        return Status._getter(self, Status.LIM_LOW_BIT)

    @lim_low.setter
    def lim_low(self, value: bool) -> None:
        Status._setter(self, Status.LIM_LOW_BIT, value=value)

    @property
    def err(self) -> bool:
        return Status._getter(self, Status.PROPAGATED_BIT)

    @err.setter
    def err(self, value: bool) -> None:
        Status._setter(self, Status.PROPAGATED_BIT, value=value)


class Signal[T: Value]:
    """Represents a value with an associated status."""

    value: T
    status: Status

    def __init__(self, value: T) -> None:
        self.value = value
        self.status = Status()

    def __repr__(self) -> str:
        return f"Signal({self.value!r})"


@dataclass
class UnparsedConnection[T: Value]:
    """Placeholder for a connection yet to be parsed."""

    compound: str
    block: str
    parameter: str

    def parse(self, emulator: Emulator) -> Connection[T]:
        return Connection(
            block=emulator.compounds[self.compound][self.block],
            parameter=self.parameter,
        )


@dataclass
class Connection[T: Value]:
    """Represents a parsed connection to a block/parameter."""

    block: EmulatedBlock
    parameter: str

    def get_value(self) -> T:
        if p := self.block.get_parameter(self.parameter):
            return p.get_value()
        else:
            description = "invalid connection"
            raise RuntimeError(description)


class Parameter[T: Value]:
    """Represents a parameter on a block."""

    inner: UnparsedConnection[T] | Connection[T] | Signal[T] | T

    def __init__(self, inner: UnparsedConnection[T] | Connection[T] | Signal[T] | T) -> None:
        self.inner = inner

    def __repr__(self) -> str:
        return repr(self.inner)

    def get_value(self) -> T:
        match self.inner:
            case UnparsedConnection():
                description = "unparsed connection"
                raise RuntimeError(description)
            case Connection():
                return self.inner.get_value()
            case Signal():
                return self.inner.value
            case T:  # noqa: F841
                return self.inner

    def assign_value(self, value: T) -> None:
        match self.inner:
            case UnparsedConnection():
                description = "unparsed connection"
                raise RuntimeError(description)
            case Connection():
                description = "can't assign value to a connected parameter"
                raise RuntimeError(description)
            case Signal():
                self.inner.value = value
            case T:  # noqa: F841
                self.inner = value


class Input[T: Value](Parameter[T]):
    """Represents an input parameter."""


class Output[T: Value](Parameter[T]):
    """Represents an output parameter."""
