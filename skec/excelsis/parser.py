from typing import Any, Optional, Union, Dict

from ..excelsis.errors import InvalidSyntaxError, Error, InvalidTypeError
from ..excelsis.nodes import BinOpNode, NumberNode, UnaryOpNode, FunctionNode, ValueOfNode, Node, EOFNode
from ..excelsis.tokens import NumberToken, EXCELSISToken, Function


class EXCELSISParser:

    def __init__(self, tokens: Dict) -> None:
        self.all_tokens = tokens
        self.tokens = None
        self.current_cell = None
        self.token_index = -1
        self.current_token = None

    def parse(self) -> Union[Dict, Error]:
        result = {}
        for y, (k, (tokens, cell)) in enumerate(self.all_tokens.items()):
            self.token_index = -1
            self.tokens = tokens
            self.current_cell = cell
            if len(self.tokens) <= 1:
                result[k] = EOFNode()
                continue
            self.advance()
            result[k] = self.function()
        return result

    def number(self) -> Union[Node, Error]:
        if isinstance(tok := self.current_token, NumberToken):
            self.advance()
            return NumberNode(tok)
        elif self.current_token is EXCELSISToken.QUESTIONMARK:
            self.advance()
            return BinOpNode(self.current_cell[0], EXCELSISToken.PIPE, self.current_cell[1])
        elif self.current_token is EXCELSISToken.DOLLAR:
            self.advance()
            return BinOpNode(0, EXCELSISToken.DOLLAR, 0)
        return InvalidSyntaxError("Expected expression!")

    def factor(self) -> Union[Node, Error]:
        tok = self.current_token
        if tok in (EXCELSISToken.PLUS, EXCELSISToken.MINUS):
            self.advance()
            return UnaryOpNode(tok, self.factor())
        elif self.current_token is EXCELSISToken.LPAREN:
            self.advance()
            expr = self.pipe()
            if self.current_token is not EXCELSISToken.RPAREN or isinstance(expr, Error):
                return InvalidSyntaxError("'[' was never closed!")
            if not isinstance(expr, BinOpNode) and expr.token is not EXCELSISToken.PIPE:
                return InvalidTypeError("Square brackets can only hold positions!")
            self.advance()
            return expr
        elif self.current_token is EXCELSISToken.LPARENSOFT:
            self.advance()
            expr = self.pipe()
            if self.current_token is not EXCELSISToken.RPARENSOFT or isinstance(expr, Error):
                return InvalidSyntaxError("'(' was never closed!")
            self.advance()
            return ValueOfNode(expr)
        return self.number()

    def term(self) -> Union[Node, Error]:
        left = self.factor()

        while self.current_token in (EXCELSISToken.MUL, EXCELSISToken.DIV, EXCELSISToken.MODULO):
            tok = self.current_token
            self.advance()
            right = self.factor()
            if isinstance(left, Error):
                return left
            if isinstance(right, Error):
                return right
            left = BinOpNode(left, tok, right)
        return left

    def expression(self) -> Union[Node, Error]:
        left = self.term()

        while self.current_token in (EXCELSISToken.PLUS, EXCELSISToken.MINUS):
            tok = self.current_token
            self.advance()
            right = self.term()
            if isinstance(left, Error):
                return left
            if isinstance(right, Error):
                return right
            left = BinOpNode(left, tok, right)
        return left

    def pipe(self) -> Union[Node, Error]:
        left = self.expression()

        if self.current_token is EXCELSISToken.PIPE:
            tok = self.current_token
            self.advance()
            right = self.expression()
            if isinstance(left, Error):
                return left
            if isinstance(right, Error):
                return right
            return BinOpNode(left, tok, right)
        return left

    def equal_sign(self) -> Union[Node, Error]:
        left = self.pipe()

        if self.current_token is EXCELSISToken.EQUALS:
            tok = self.current_token
            self.advance()
            right = self.pipe()
            if isinstance(left, Error):
                return left
            if isinstance(right, Error):
                return right
            return BinOpNode(left, tok, right)
        return left

    def function(self) -> Union[Node, Error]:
        if isinstance(self.current_token, Error):
            return self.current_token
        if isinstance(self.current_token, Function):
            tok = self.current_token
            self.advance()
            args = [self.equal_sign()]
            while self.current_token is EXCELSISToken.BINAND:
                self.advance()
                args.append(self.equal_sign())
                for arg in args:
                    if isinstance(arg, Error):
                        return arg
            return FunctionNode(tok, args)
        return self.equal_sign()

    def advance(self) -> None:
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

