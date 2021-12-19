from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Union, Any, Tuple

from skec.excelsis.errors import InvalidTypeError, Error


@dataclass
class CellPosition:

    i: int
    j: int

    def get_pos(self) -> Tuple[int, int]:
        return self.i, self.j

    def add(self, a) -> Union[CellPosition, Error]:
        if isinstance(a, CellPosition):
            return CellPosition(self.i + a.i, self.j + a.j)
        elif isinstance(a, int):
            return CellPosition(self.i + a, self.j + a)
        return InvalidTypeError("Invalid operand type on cell position!")

    def sub(self, a) -> Union[CellPosition, Error]:
        if isinstance(a, CellPosition):
            return CellPosition(self.i - a.i, self.j - a.j)
        elif isinstance(a, int):
            return CellPosition(self.i - a, self.j - a)
        return InvalidTypeError("Invalid operand type on cell position!")

    def mul(self, a) -> Union[CellPosition, Error]:
        if isinstance(a, CellPosition):
            return InvalidTypeError("Cannot multiply cell position with cell position!")
        elif isinstance(a, int):
            return CellPosition(self.i * a, self.j * a)
        return InvalidTypeError("Invalid operand type on cell position!")

    def div(self, a) -> Union[CellPosition, Error]:
        if isinstance(a, CellPosition):
            return InvalidTypeError("Cannot divide cell position with cell position!")
        elif isinstance(a, int):
            return CellPosition(self.i // a, self.j // a)
        return InvalidTypeError("Invalid operand type on cell position!")


class EXCELSISToken(Enum):

    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    MODULO = auto()
    EQUALS = auto()
    SING_QUOTE = auto()
    PIPE = auto()
    RPAREN = auto()
    LPAREN = auto()
    RPARENSOFT = auto()
    LPARENSOFT = auto()
    BINAND = auto()
    EOF = auto()
    QUESTIONMARK = auto()
    HASHTAG = auto()


@dataclass
class NumberToken:

    value: Union[int, float]


@dataclass
class FunctionToken:

    name: str


class Function:

    def __init__(self, name, args) -> None:
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f"Function(name={self.name}, args=...)"


@dataclass
class FuncArgs:

    arguments: list[Any]
    types: list[Any]

    def __post_init__(self) -> None:
        if len(self.arguments) != len(self.types):
            raise ValueError("Arguments and types must be the same length!")
        for i, arg in enumerate(self.arguments):
            if isinstance(self.types[i], list):
                if all(list(map(lambda x: not isinstance(arg, x), self.types[i]))):
                    self.invalid_arguments = True
            elif not isinstance(arg, self.types[i]):
                self.invalid_arguments = True


class Functions:

    GOTO = Function("GOTO", FuncArgs(["position"], [CellPosition]))
    PR = Function("PR", FuncArgs(["bin"], [[int, float]]))
    PRB = Function("PRB", FuncArgs(["bin"], [int]))
    INT = Function("INT", FuncArgs(["int"], [float]))
    FLOAT = Function("FLOAT", FuncArgs(["float"], [int]))
    W = Function("W", FuncArgs(["position", "value"], [CellPosition, int]))
    INPUT = Function("INPUT", FuncArgs([], []))


class EXCELSISCell:

    def __init__(self, tokens, value) -> None:
        self.tokens = tokens
        self.value = value

    def __repr__(self) -> str:
        return f"EXCELSISCell(tokens={self.tokens}, value={self.value})"
