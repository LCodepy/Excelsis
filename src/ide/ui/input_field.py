import time
from threading import Timer
from typing import Tuple

import pygame

from ..events.buttons import Buttons
from ..main.config import Config
from ..ui.label import Label


class InputField:

    def __init__(self, app, x: int, y: int, text: str, font: pygame.font.Font, blink_time_secs: float = None,
                 centerx: bool = True, centery: bool = True, max_width: int = 100, max_height: int = 60,
                 width: int = Config.CELL_SIZE[0], height: int = Config.CELL_SIZE[1]) -> None:
        self.app = app
        self.__x = x
        self.__y = y
        self.text = text
        self.max_width = max_width
        self.max_height = max_height
        self.width = width
        self.height = height

        self.label = Label(
            app,
            text,
            x, y,
            font,
            color=Config.BOARD_COLOR,
            width=100,
            centerx=centerx, centery=centery,
            max_width=self.max_width, max_height=self.max_height
        )

        self.__show_cursor = True
        self.__cursor_active = False
        self.blink_secs = blink_time_secs or Config.CURSOR_BLINK_TIME_SECS
        self.__cursor_timer = Timer(self.blink_secs, self.revert_cursor)

        self.__focused = False

        self.__last_del_time = 0

    def update(self) -> None:
        if not self.__focused:
            return

        if (
            (key := self.app.event_handler.key_just_pressed()) is not None and
            not self.app.event_handler.keydown(pygame.K_ESCAPE) and
            not self.app.event_handler.keydown(pygame.K_RCTRL) and
            (not self.app.event_handler.keydown(pygame.K_LCTRL) or
             self.app.event_handler.keydown(pygame.K_RALT))
        ):
            name = pygame.key.name(key)
            form_name = name.replace("[", "").replace("]", "")
            if len(form_name) == 1:
                if self.app.event_handler.keydown(pygame.K_RSHIFT) or self.app.event_handler.keydown(pygame.K_LSHIFT):
                    form_name = form_name.upper()
                    if form_name == "8":
                        form_name = "("
                    elif form_name == "9":
                        form_name = ")"
                    elif form_name == "+":
                        form_name = "*"
                    elif form_name == "0":
                        form_name = "="
                    elif form_name == "6":
                        form_name = "&"
                    elif form_name == "5":
                        form_name = "%"
                    elif form_name == ".":
                        form_name = ":"
                    elif form_name == "'":
                        form_name = "?"
                    elif form_name == "3":
                        form_name = "#"
                    elif form_name == "4":
                        form_name = "$"
                if self.app.event_handler.keydown(pygame.K_RALT):
                    if form_name == "w":
                        form_name = "|"
                    elif form_name == "q":
                        form_name = "\\"
                    elif form_name == "f":
                        form_name = "["
                    elif form_name == "g":
                        form_name = "]"
                self.text += form_name
            elif name == "space":
                self.text += " "

        if self.app.event_handler.keydown(pygame.K_BACKSPACE) and time.time() - self.__last_del_time > Config.DEL_TIMER:
            self.__last_del_time = time.time()
            self.text = self.text[:-1]

        self.label.update_text(self.text)

        self.update_cursor()

    def update_cursor(self) -> None:
        if not self.__show_cursor:
            return

        if not self.__cursor_timer.is_alive():
            self.__cursor_timer = Timer(self.blink_secs, self.revert_cursor)
            self.__cursor_timer.start()

    def render(self, canvas=None) -> None:
        canvas = canvas or self.app.canvas

        if self.__focused:
            self.label.render(canvas=canvas)
        else:
            self.label.render_rect(self.__x - self.max_width // 2, self.__y - self.max_height // 2, self.width, self.height, canvas=canvas)

        if not self.__focused:
            return

        if self.__cursor_active:
            x, y = self.label.get_end_pos()
            pygame.draw.line(canvas, Config.BOARD_COLOR, (x, y - 2), (x, y + self.label.height), 3)

    def set_pos(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y
        self.label.x = x
        self.label.y = y

    def get_pos(self) -> Tuple[int, int]:
        return self.__x, self.__y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.__x, self.__y, self.width, self.height)

    def show_cursor(self, b: bool) -> None:
        self.__show_cursor = b

    def revert_cursor(self) -> None:
        self.__cursor_active = not self.__cursor_active

    def focus(self, b: bool) -> None:
        self.__focused = b

    def hovering(self) -> bool:
        x, y = self.app.event_handler.pos()
        return self.__x < x < self.__x + self.width and self.__y < y < self.height

    def update_focus_on_click(self) -> None:
        if self.app.event_handler.just_pressed(Buttons.LEFT):
            self.__focused = self.hovering()

