import time
from collections import defaultdict
from typing import Tuple, Optional

import pygame

from .buttons import Buttons


class EventHandler:

    def __init__(self) -> None:
        self.__has_quit: bool = False

        self.__presses: dict[int, bool] = {Buttons.LEFT: False, Buttons.MIDDLE: False, Buttons.RIGHT: False}
        self.__releases: dict[int, bool] = {Buttons.LEFT: False, Buttons.MIDDLE: False, Buttons.RIGHT: False}
        self.__holds: dict[int, float] = {Buttons.LEFT: 0, Buttons.MIDDLE: 0, Buttons.RIGHT: 0}
        self.__start__holds: dict[int, float] = {Buttons.LEFT: 0, Buttons.MIDDLE: 0, Buttons.RIGHT: 0}

        self.__keys_pressed: defaultdict[int, bool] = defaultdict(lambda: False)
        self.__key_just_pressed: Optional[int] = None
        self.__keys_pressed_times: defaultdict[int, float] = defaultdict(lambda: 0)

        self.__rel = (0, 0)

    def update(self) -> None:
        self.__reset()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__has_quit = True
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.__presses[event.button] = True
                self.__start__holds[event.button] = time.time()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.__releases[event.button] = True
                self.__start__holds[event.button] = 0
                self.__holds[event.button] = 0

            elif event.type == pygame.KEYDOWN:
                self.__keys_pressed[event.key] = True
                self.__keys_pressed_times[event.key] = time.time()
                self.__key_just_pressed = event.key

            elif event.type == pygame.KEYUP:
                self.__keys_pressed[event.key] = False
                self.__keys_pressed_times[event.key] = 0

            elif event.type == pygame.MOUSEMOTION:
                self.__rel = event.rel

        for k, sht in self.__start__holds.items():
            if sht != 0:
                self.__holds[k] = time.time() - sht

    def __reset(self) -> None:
        self.__presses = {Buttons.LEFT: False, Buttons.MIDDLE: False, Buttons.RIGHT: False}
        self.__releases = {Buttons.LEFT: False, Buttons.MIDDLE: False, Buttons.RIGHT: False}
        self.__rel = (0, 0)
        self.__key_just_pressed = None

    def pressed(self, b: int) -> bool:
        return pygame.mouse.get_pressed()[b - 1]

    def just_pressed(self, b: int) -> bool:
        return self.__presses[b]

    def just_released(self, b: int) -> bool:
        return self.__releases[b]

    def held(self, b: int) -> float:
        return self.__holds[b]

    def is_held(self, b: int) -> bool:
        return self.__holds[b] != 0

    def keys_pressed(self) -> defaultdict:
        return self.__keys_pressed

    def keydown(self, k: int) -> bool:
        return self.__keys_pressed[k]

    def tkeydown(self, k: int) -> float:
        if self.__keys_pressed_times[k] == 0:
            return 0.0
        return time.time() - self.__keys_pressed_times[k]

    def key_just_pressed(self) -> Optional[int]:
        return self.__key_just_pressed

    def moved(self) -> Tuple[int, int]:
        return self.__rel

    def dragged(self, b: int) -> Tuple[int, int]:
        if self.is_held(b):
            return self.__rel
        return 0, 0

    def pos(self) -> Tuple[int, int]:
        return pygame.mouse.get_pos()

    def quit(self) -> bool:
        return self.__has_quit
