import dataclasses
from abc import ABC
from dataclasses import dataclass


class Error(ABC):

    def __init__(self, description="") -> None:
        self.description = description
        self.name = "Error"

    def __repr__(self) -> str:
        return f"{self.name}: {self.description}"


class InvalidSyntaxError(Error):

    def __init__(self, description) -> None:
        super().__init__(description)
        self.name = "Invalid Syntax Error"


class InvalidTypeError(Error):

    def __init__(self, description="Invalid Type: ") -> None:
        super().__init__(description)
        self.name = "Invalid Type Error"


class InvalidArgumentError(Error):

    def __init__(self, description="Invalid Argument: ") -> None:
        super().__init__(description)
        self.name = "Invalid Argument Error"

