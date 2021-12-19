import copy
from collections import defaultdict
from typing import Union, Tuple, Callable, Any

from ..excelsis.errors import Error, InvalidTypeError, InvalidSyntaxError
from ..excelsis.log import Log
from ..excelsis.nodes import Node, NumberNode, UnaryOpNode, BinOpNode, FunctionNode, ValueOfNode, EOFNode
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

    def run(self, is_running: Callable) -> None:
        Log.i("", "")
        Log.i("N", "----------------------------------")
        while True:
            if not is_running():
                break
            Log.i("", "")
            Log.i("CELL", str(self.current_cell))
            Log.i("CURRENT CELL VALUE", str(self.parse_results[self.current_cell]))
            c = self.current_cell
            self.interp = self.interpret(self.parse_results[self.current_cell])
            if self.interp not in (self.HOLDER, self.SKIP_INCREMENT):
                self.interpreted[self.current_cell] = self.interp
            Log.i("INTERPRET", str(self.interp))
            Log.i("PARSE RESULTS", str(self.parse_results))
            Log.i("INTERPRETED", str(self.interpreted))
            Log.i("INTERPRETED VALUE", str(self.interpreted[c]))
            Log.i("", "")
            if self.interp is not self.SKIP_INCREMENT:
                self.increment()
            if isinstance(self.interp, Error):
                print(self.interp)
                break
            if self.eof:
                break

        print()
        print("PROGRAM FINISHED!")
        print()

        self.finished = True

    def interpret(self, node: Union[int, float, CellPosition, Error]) -> Union[int, float, CellPosition, Error]:
        if isinstance(node, (type(self.SKIP_INCREMENT), int, float, CellPosition, Error)):
            return node
        return self.__getattribute__("interpret_" + node.name)(node)

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
            return left + right
        elif node.token is EXCELSISToken.MINUS:
            return left - right
        elif node.token is EXCELSISToken.MUL:
            return left * right
        elif node.token is EXCELSISToken.DIV:
            return left / right
        elif node.token is EXCELSISToken.MODULO:
            return left % right
        elif node.token is EXCELSISToken.EQUALS:
            return int(left == right)
        elif node.token is EXCELSISToken.PIPE:
            if isinstance(left, int) or isinstance(right, int):
                return CellPosition(left, right)
            return InvalidTypeError("Cell pos can only be integer!")

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
            return self.interpret(self.parse_results[interp.get_pos()] or 0)

    def interpret_EOFNode(self, node: EOFNode) -> EOFNode:
        self.eof = True
        return node

    def increment(self) -> None:
        if self.current_cell[0] < self.bottom_right()[0]:
            self.current_cell = (self.current_cell[0] + 1, self.current_cell[1])
        else:
            self.eof = True

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

