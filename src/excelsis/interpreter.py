import copy
from collections import defaultdict
from typing import Union, Tuple, Callable, Any

from ..excelsis.errors import Error, InvalidTypeError, RTError
from ..excelsis.nodes import NumberNode, UnaryOpNode, BinOpNode, FunctionNode, ValueOfNode, EOFNode
from ..excelsis.tokens import EXCELSISToken, CellPosition


class EXCELSISInterpreter:

    def __init__(self, parse_results) -> None:
        self.parse_results: defaultdict[Any] = defaultdict(lambda: EOFNode())
        for k, v in parse_results.items():
            self.parse_results[k] = v
        self.interpreted = copy.deepcopy(self.parse_results)
        self.current_cell = (0, 0)
        self.eof = False
        self.interp = None
        self.results = {}
        self.HOLDER = type("HOLDER", (), {})
        self.SKIP_INCREMENT = type("SKIP_INCREMENT", (), {})
        self.finished = False
        self.previous_cell = None
        self.last_cell = (0, 0)

    def run(self, is_running: Callable) -> None:
        while True:
            if not is_running():
                break
            self.previous_cell = self.current_cell
            c = self.current_cell
            self.interp = self.interpret(self.parse_results[self.current_cell])
            if self.interp not in (self.HOLDER, self.SKIP_INCREMENT):
                self.interpreted[self.current_cell] = self.interp
            self.last_cell = c
            if self.interp is not self.SKIP_INCREMENT:
                self.increment()
            if isinstance(self.interp, Error):
                print(self.interp)
                break
            if self.eof:
                break

        print()
        print()
        print("PROGRAM FINISHED!")
        print()

        self.finished = True

    def interpret(self, node: Union[int, float, CellPosition, Error]) -> Union[int, float, CellPosition, Error]:
        if isinstance(node, (type(self.SKIP_INCREMENT), int, float, CellPosition, Error)):
            return node
        try:
            return self.__getattribute__("interpret_" + node.name)(node)
        except RecursionError:
            return RTError("Maximum recursion depth exceeded (probably due to circular reference)!")

    def interpret_NumberNode(self, node: NumberNode) -> Union[int, float, Error]:
        return node.token.value

    def interpret_UnaryOpNode(self, node: UnaryOpNode) -> Union[int, float, Error]:
        n = self.interpret(node.node)
        if isinstance(n, Error):
            return n
        return -1 * n if node.token is EXCELSISToken.MINUS else n

    def interpret_BinOpNode(self, node: BinOpNode) -> Union[int, float, CellPosition, Error]:
        left = self.interpret(node.left)
        right = self.interpret(node.right)

        if isinstance(left, Error):
            return left
        if isinstance(right, Error):
            return right

        if node.token is EXCELSISToken.PLUS:
            return self.add(left, right)
        elif node.token is EXCELSISToken.MINUS:
            return self.sub(left, right)
        elif node.token is EXCELSISToken.MUL:
            return self.mul(left, right)
        elif node.token is EXCELSISToken.DIV:
            return self.div(left, right)
        elif node.token is EXCELSISToken.MODULO:
            return self.modulo(left, right)
        elif node.token is EXCELSISToken.EQUALS:
            return int(left == right)
        elif node.token is EXCELSISToken.PIPE:
            if isinstance(left, int) or isinstance(right, int):
                return CellPosition(left, right)
            return InvalidTypeError("Cell pos can only be integer!")
        elif node.token is EXCELSISToken.DOLLAR:
            return CellPosition(self.last_cell[0], self.last_cell[1])

        return InvalidTypeError("Unsupported operand!")

    def interpret_FunctionNode(self, node: FunctionNode) -> Union[int, float, CellPosition, Error]:
        interps = []
        for i in range(len(node.args)):
            interps.append(self.interpret(node.args[i]))

        node.interp_args.clear()
        for interp in interps:
            if cm := node.compile(*interps):
                return cm
            else:
                node.feed(interp)

        return self.interpret(node.execute(self) or self.HOLDER) or self.HOLDER

    def interpret_ValueOfNode(self, node: ValueOfNode) -> Union[int, float, CellPosition, Error]:
        interp = self.interpret(node.expr)

        if isinstance(interp, (int, float, Error)):
            return interp
        elif isinstance(interp, CellPosition):
            return self.interpret(p if not isinstance(p := self.parse_results[interp.get_pos()], EOFNode) else 0)

    def interpret_EOFNode(self, node: EOFNode) -> EOFNode:
        self.eof = True
        return node

    def increment(self) -> None:
        if self.current_cell[0] < self.bottom_right()[0]:
            self.current_cell = (self.current_cell[0] + 1, self.current_cell[1])
        else:
            self.eof = True

    # Other

    def top_left(self) -> Tuple[int, int]:
        mn = float("inf")
        m = None
        for k, v in self.parse_results.items():
            if k[0] + k[1] < mn:
                mn = k[0] + k[1]
                m = k
        return m

    def bottom_right(self) -> Tuple[int, int]:
        mx = -float("inf")
        m = None
        for k, v in self.parse_results.items():
            if k[0] + k[1] > mx:
                mx = k[0] + k[1]
                m = k
        return m

    def add(self, a, b) -> Union[Error, CellPosition, int, float]:
        if isinstance(a, CellPosition):
            return a.add(b)
        elif isinstance(b, CellPosition):
            return b.add(a)
        return a + b

    def sub(self, a, b) -> Union[Error, CellPosition, int, float]:
        if isinstance(a, CellPosition):
            return a.sub(b)
        elif isinstance(b, CellPosition):
            return b.sub(a)
        return a - b

    def mul(self, a, b) -> Union[Error, CellPosition, int, float]:
        if isinstance(a, CellPosition):
            return a.mul(b)
        elif isinstance(b, CellPosition):
            return b.mul(a)
        return a * b

    def div(self, a, b) -> Union[Error, CellPosition, int, float]:
        if b == 0:
            return 42
        if isinstance(a, CellPosition):
            return a.div(b)
        if isinstance(b, CellPosition):
            return b.div(a)
        return a / b

    def modulo(self, a, b) -> Union[Error, CellPosition, Error, int, float]:
        if b == 0:
            return 42
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a % b
        return InvalidTypeError(f"Unsupported operand '%'!")

