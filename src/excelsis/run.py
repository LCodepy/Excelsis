from collections import defaultdict
from threading import Thread
from typing import Callable

from ..excelsis.interpreter import EXCELSISInterpreter
from ..excelsis.lexer import EXCELSISLexer
from ..excelsis.parser import EXCELSISParser


class EXCELSISRunner:

    def __init__(self, cells: defaultdict) -> None:
        self.cells = cells
        self.thread = None
        self.disabled = False
        self.interpreter = None

    def run(self, process_killed: Callable) -> None:
        if self.disabled:
            return

        lexer = EXCELSISLexer(self.cells)
        tokens = lexer.execute()

        parser = EXCELSISParser(tokens)
        parsed_tokens = parser.parse()

        self.interpreter = EXCELSISInterpreter(parsed_tokens)
        self.thread = Thread(target=self.interpreter.run, args=(process_killed, ))
        self.thread.start()

    def stop(self) -> None:
        self.thread.join()

    def disable(self) -> None:
        self.disabled = not self.disabled
