from typing import Tuple


class Config:

    TITLE: str = "Excelsis | Version 1.0 Beta"
    WINDOW_SIZE: Tuple[int, int] = 1000, 830
    CANVAS_SIZE: Tuple[int, int] = 1000, 800
    FPS: int = 60
    CELL_SIZE: Tuple[int, int] = 100, 80
    BOARD_COLOR: Tuple[int, int, int] = (0, 180, 31)
    MIN_DRAG_DISTANCE: float = 10.0
    CURSOR_BLINK_TIME_SECS: float = 0.5
    MIN_MOUSE_HOLD_TIME: float = 0.1
    DEL_TIMER: float = 0.11
    SHOW_GRID: bool = False

