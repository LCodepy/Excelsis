from collections import defaultdict
from typing import Tuple, Union, Any

from ..excelsis.errors import Error, InvalidSyntaxError
from ..excelsis.grammar import Grammar
from ..excelsis.tokens import EXCELSISToken, NumberToken, FunctionToken, Functions
from skec.ide.components.cells import Cell
from skec.ide.utils.arrays import cols2d


class EXCELSISLexer:

    def __init__(self, cells: defaultdict[Tuple[int, int], Cell]) -> None:
        self.cells = cells

        self.current_char = None
        self.current_pos = -1
        self.current_code = None
        self.current_cell = None

    def execute(self) -> dict[list[EXCELSISToken]]:
        lex_res = {}
        for col in cols2d(self.format_cells()):
            for cell in col:
                lex_res[cell.get_pos()] = self.read_cell(cell)
        return lex_res

    def format_cells(self) -> list[list[Cell]]:
        mn_y = 0
        mn_x = 0
        mx_y = 0
        mx_x = 0
        for pos in self.cells.keys():
            if pos[0] < mn_y:
                mn_y = pos[0]
            if pos[0] > mx_y:
                mx_y = pos[0]
            if pos[1] < mn_x:
                mn_x = pos[1]
            if pos[1] > mx_x:
                mx_x = pos[1]

        return [[Cell(j, i, self.cells[i, j].code if (i, j) in self.cells else "") for j in range(mn_x, mx_x + 1)] for i
                in range(mn_y, mx_y + 1)]

    def read_cell(self, cell: Cell) -> list[Any]:
        code = cell.code
        self.current_code = code
        self.current_cell = cell
        self.current_pos = -1

        tokens = []

        while self.current_pos < len(code) - 1:
            self.advance()

            if self.current_char == " ":
                continue

            found = False

            if self.current_char.isdigit():
                found = True
                tokens.append(self.find_number())
            if self.current_char.isupper() and self.current_char in Grammar.ALLOWED_CHARACTERS_FOR_FN_NAMES:
                tokens.append(self.find_function())
                found = True

            if self.current_char == "+":
                tokens.append(EXCELSISToken.PLUS)
            elif self.current_char == "-":
                tokens.append(EXCELSISToken.MINUS)
            elif self.current_char == "*":
                tokens.append(EXCELSISToken.MUL)
            elif self.current_char == "/":
                tokens.append(EXCELSISToken.DIV)
            elif self.current_char == "%":
                tokens.append(EXCELSISToken.MODULO)
            elif self.current_char == "|":
                tokens.append(EXCELSISToken.PIPE)
            elif self.current_char == "'":
                tokens.append(EXCELSISToken.SING_QUOTE)
            elif self.current_char == "=":
                tokens.append(EXCELSISToken.EQUALS)
            elif self.current_char == "[":
                tokens.append(EXCELSISToken.LPAREN)
            elif self.current_char == "]":
                tokens.append(EXCELSISToken.RPAREN)
            elif self.current_char == "&":
                tokens.append(EXCELSISToken.BINAND)
            elif self.current_char == "(":
                tokens.append(EXCELSISToken.LPARENSOFT)
            elif self.current_char == ")":
                tokens.append(EXCELSISToken.RPARENSOFT)
            elif self.current_char == "?":
                tokens.append(EXCELSISToken.QUESTIONMARK)
            elif self.current_char == "#":
                break
            elif not found:
                tokens.append(InvalidSyntaxError("Illegal Character!"))

        tokens.append(EXCELSISToken.EOF)
        return [tokens, cell.get_pos()]

    def find_number(self) -> Union[NumberToken, Error]:
        n = ""
        n_dots = 0
        while (self.current_char.isdigit() or self.current_char == ".") and self.current_pos < len(self.current_code):
            n += self.current_char

            if self.current_char == ".":
                n_dots += 1
            if n_dots > 1:
                return InvalidSyntaxError("too many dots in a number!")

            self.advance()

        return NumberToken(eval(n))

    def find_function(self) -> Union[FunctionToken, Error]:
        f = ""
        while self.current_char not in (" ", "#") and self.current_pos < len(self.current_code):
            f += self.current_char

            self.advance()

        if f in Functions.__dict__:
            return Functions().__getattribute__(f)
        return InvalidSyntaxError(f"No function called {f!r}!")

    def advance(self) -> None:
        self.current_pos += 1
        if self.current_pos < len(self.current_code):
            self.current_char = self.current_code[self.current_pos]
