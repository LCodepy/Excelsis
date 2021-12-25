import sys
from abc import ABC
from typing import Optional, Any

from ..excelsis.errors import Error, InvalidArgumentError, InvalidTypeError, InvalidSyntaxError
from ..excelsis.log import Log
from ..excelsis.tokens import NumberToken


class Node(ABC):

    def __init__(self, token) -> None:
        self.token = token
        self.name = "Node"


class NumberNode(Node):

    def __init__(self, token) -> None:
        super().__init__(token)
        self.name = "NumberNode"

    def __repr__(self) -> str:
        return str(self.token)


class UnaryOpNode(Node):

    def __init__(self, token, node) -> None:
        self.node = node
        super().__init__(token)
        self.name = "UnaryOpNode"

    def __repr__(self) -> str:
        return f"({self.token}, {self.node})"


class BinOpNode(Node):

    def __init__(self, left, token, right) -> None:
        self.left = left
        self.right = right
        super().__init__(token)
        self.name = "BinOpNode"

    def __repr__(self) -> str:
        return f"({self.left}, {self.token}, {self.right})"


class ValueOfNode(Node):

    def __init__(self, expr) -> None:
        self.expr = expr
        super().__init__(None)
        self.name = "ValueOfNode"

    def __repr__(self) -> str:
        return f"ValueOf({self.expr})"


class FunctionNode(Node):

    def __init__(self, function, args) -> None:
        self.function = function
        self.args = args if args[0] is not None else []
        super().__init__(function)
        self.name = "FunctionNode"

        self.interp_args = []

    def compile(self, *args) -> Optional[Error]:
        if (
            len(args) == 1 and
            isinstance(args[0], InvalidSyntaxError) and
            args[0].description == "Expected expression!" and
            len(self.function.args.arguments) == 0
        ):
            args = []
        for i, arg in enumerate(args):
            if isinstance(arg, Error):
                return InvalidArgumentError("Too few arguments!")
            if isinstance(self.function.args.types[i], list):
                if all(list(map(lambda x: not isinstance(arg, x), self.function.args.types[i]))):
                    return InvalidArgumentError("Invalid argument type!")
            elif not isinstance(arg, self.function.args.types[i]):
                return InvalidArgumentError("Invalid argument type!")

    def feed(self, arg) -> None:
        self.interp_args.append(arg)

    def execute(self, context) -> Any:
        if self.function.name == "GOTO":
            context.current_cell = self.interp_args[0].get_pos()
            # context.interp = context.interpret(context.parse_results[context.current_cell])
            return context.SKIP_INCREMENT
        elif self.function.name == "INPUT":
            try:
                input_ = float(input())
                if str(input_).endswith(".0"):
                    input_ = int(input_)
            except ValueError:
                input_ = InvalidTypeError("Input type must be integer or float.")
            context.parse_results[context.current_cell] = input_
            return context.parse_results[context.current_cell]
        elif self.function.name == "W":
            if context.previous_cell == self.interp_args[0].get_pos():
                return InvalidArgumentError("Position to write cannot be same as cell position.")
            Log.i("INTERP ARGS", self.interp_args[1])
            context.interpreted[self.interp_args[0].get_pos()] = self.interp_args[1]
            context.parse_results[self.interp_args[0].get_pos()] = self.interp_args[1]
            Log.i("PARSE RESULTS 2", context.parse_results)
        elif self.function.name == "PR":
            sys.stdout.write(str(self.interp_args[0]))
        elif self.function.name == "PRB":
            sys.stdout.write(chr(self.interp_args[0]))
        elif self.function.name == "INT":
            context.parse_results[context.current_cell] = int(self.interp_args[0])
        elif self.function.name == "FLOAT":
            context.parse_results[context.current_cell] = float(self.interp_args[0])

    def __repr__(self) -> str:
        return repr(self.function).replace("...)", str(self.args)) + "  |=|  " + repr(self.function.args)


class EOFNode(Node):

    def __init__(self) -> None:
        super().__init__(None)
        self.name = "EOFNode"

    def __repr__(self) -> str:
        return f"EOF"
