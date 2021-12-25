from typing import Tuple


class Cell:

    def __init__(self, x: int, y: int, code: str = "") -> None:
        self.x = x
        self.y = y
        self.code = code

    def get_pos(self) -> Tuple[int, int]:
        return self.y, self.x

    def __repr__(self) -> str:
        return f"Cell(x={self.x}, y={self.y}, code={self.code})"

