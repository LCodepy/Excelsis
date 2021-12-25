import time
from collections import defaultdict
from typing import Tuple

import pygame

from ..components.cells import Cell
from ..events.buttons import Buttons
from ..main.config import Config
from ..ui.input_field import InputField
from ..ui.label import Label


class Board:

    def __init__(self, app) -> None:
        self.app = app

        self.cells = defaultdict(None)

        self.x_offset = 550
        self.y_offset = 450

        self.min_x_gap = 40
        self.min_y_gap = 40

        self.x_fill = 0
        self.y_fill = 40

        self.board_canvas = pygame.Surface((1000 - self.min_x_gap, 800 - self.min_y_gap))

        self.input_fields = defaultdict(None)
        self.current_cell = (0, 0)
        self.create_cell(0, 0)

        self.__last_held = 0

        self.__keytime_held: defaultdict = defaultdict(lambda: 0.0)

    def update(self) -> None:
        for k, v in self.input_fields.items():
            lx, ly = self.get_left_corner(k[1], k[0])
            v.set_pos(lx + 40, ly + 40)
            if k == self.current_cell:
                v.update()

        self.cells[self.current_cell].code = self.input_fields[self.current_cell].text

        self.__last_held = max(self.app.event_handler.held(Buttons.LEFT), self.__last_held)

        self.check_arrow_movement()
        # self.check_for_cell_clicks()

        if self.app.event_handler.just_released(Buttons.LEFT):
            self.__last_held = 0

    def check_for_cell_clicks(self) -> None:
        if (
            self.__last_held < Config.MIN_MOUSE_HOLD_TIME and self.app.event_handler.just_released(Buttons.LEFT) and
            ((d := self.app.event_handler.dragged(Buttons.LEFT))[0] ** 2 + d[1] ** 2) < Config.MIN_DRAG_DISTANCE ** 2
        ):
            j, i = self.get_cell_pos(*self.app.event_handler.pos())

            self.create_cell(i, j)

    def check_arrow_movement(self) -> None:
        moved = True
        i = j = 0
        if self.app.event_handler.key_just_pressed() == pygame.K_UP or self.get_key_held_by_timer(pygame.K_UP):
            i, j = self.current_cell[0] - 1, self.current_cell[1]
            if self.input_fields[self.current_cell].get_pos()[1] < 250:
                self.y_offset += 80
        elif self.app.event_handler.key_just_pressed() == pygame.K_DOWN or self.get_key_held_by_timer(pygame.K_DOWN):
            i, j = self.current_cell[0] + 1, self.current_cell[1]
            if self.input_fields[self.current_cell].get_pos()[1] > 600:
                self.y_offset -= 80
        elif self.app.event_handler.key_just_pressed() == pygame.K_RIGHT or self.get_key_held_by_timer(pygame.K_RIGHT):
            i, j = self.current_cell[0], self.current_cell[1] + 1
            if self.input_fields[self.current_cell].get_pos()[0] > 800:
                self.x_offset -= 100
        elif self.app.event_handler.key_just_pressed() == pygame.K_LEFT or self.get_key_held_by_timer(pygame.K_LEFT):
            i, j = self.current_cell[0], self.current_cell[1] - 1
            if self.input_fields[self.current_cell].get_pos()[0] < 250:
                self.x_offset += 100
        else:
            moved = False

        if moved:
            self.create_cell(i, j)

    def get_key_held_by_timer(self, k: int) -> bool:
        if time.time() - self.__keytime_held[k] > Config.DEL_TIMER and self.app.event_handler.tkeydown(k) > 0.3:
            self.__keytime_held[k] = time.time()
            return True
        return False

    def create_cell(self, i: int, j: int) -> None:
        if (i, j) not in self.cells:
            self.cells[i, j] = Cell(j, i)

            code = self.cells[i, j].code
            x, y = self.get_left_corner(j, i)
            self.input_fields[i, j] = InputField(self.app, x + 40, y + 40, code, self.app.assets.font18)

        if self.current_cell is not None:
            self.input_fields[self.current_cell].focus(False)
        self.input_fields[i, j].focus(True)

        self.current_cell = (i, j)

    def render(self) -> None:
        self.app.canvas.blit(self.board_canvas, (self.min_x_gap, self.min_y_gap))

        for k, v in self.input_fields.items():
            if k == self.current_cell:
                pygame.draw.rect(self.app.canvas, Config.BOARD_COLOR,
                                 [v.get_pos()[0] - 50, v.get_pos()[1] - 30, *Config.CELL_SIZE], 6)
            v.render()

        self.render_fill()
        self.render_cells()

    def render_fill(self) -> None:
        pygame.draw.rect(self.app.canvas,
                         (0, 0, 0),
                         [0, self.min_x_gap, self.x_fill, Config.WINDOW_SIZE[0] - self.min_x_gap])
        pygame.draw.rect(self.app.canvas,
                         (0, 0, 0),
                         [0, 0, Config.WINDOW_SIZE[0], self.y_fill])

    def render_cells(self) -> None:
        self.board_canvas = pygame.Surface(Config.WINDOW_SIZE)

        if Config.SHOW_GRID:
            self.render_grid()

        mx = 0
        for y in range(0, self.board_canvas.get_height() + 1, Config.CELL_SIZE[1]):
            if y == 0: continue
            _, i = self.get_cell_pos(0, y - self.min_y_gap - 10)
            self.app.canvas.blit(t := Label.text(self.app.assets.font24, str(i + 1), color=Config.BOARD_COLOR),
                                 (10, y + int(self.y_offset % 80) - t.get_height() // 2))
            if t.get_width() > mx:
                mx = t.get_width()

        self.x_fill = mx + 20

        for x in range(0, self.board_canvas.get_width() + 1, Config.CELL_SIZE[0]):
            if x == 0: continue
            j, _ = self.get_cell_pos(x - 100, 0)
            self.app.canvas.blit(t := Label.text(self.app.assets.font24, str(j + 1), color=Config.BOARD_COLOR),
                                 (x + int(self.x_offset % 100) - t.get_width(), 10))

    def render_grid(self) -> None:
        for y in range(0, self.board_canvas.get_height() + 1, Config.CELL_SIZE[1]):
            pygame.draw.line(self.board_canvas,
                             Config.BOARD_COLOR,
                             (self.min_x_gap, max(y + int(self.y_offset % 80), self.min_y_gap)),
                             (self.board_canvas.get_width(), max(y + int(self.y_offset % 80), self.min_y_gap)),
                             2)
        for x in range(0, self.board_canvas.get_width() + 1, Config.CELL_SIZE[0]):
            pygame.draw.line(self.board_canvas,
                             Config.BOARD_COLOR,
                             (max(x + int(self.x_offset % 100), self.min_x_gap), self.min_y_gap),
                             (max(x + int(self.x_offset % 100), self.min_x_gap), self.board_canvas.get_height()),
                             2)

    def get_cell_pos(self, x: int, y: int) -> Tuple[int, int]:
        return (x - self.x_offset + self.min_x_gap + 10) // 100, (y - self.y_offset + self.min_y_gap + 10) // 80

    def get_left_corner(self, j: int, i: int) -> Tuple[int, int]:
        return 100 * j + self.x_offset - self.min_x_gap - 10, 80 * i + self.y_offset - self.min_y_gap - 10

    def create_input_fields(self, inp_fs):
        for k, v in inp_fs:
            x, y = self.get_left_corner(k[1], k[0])
            self.input_fields[k] = InputField(self.app, x + 40, y + 40, v, self.app.assets.font18)
