import os
import pickle

import pygame

from src.excelsis.run import EXCELSISRunner
from ..components.board import Board
from ..gfx.assets import Assets
from ..main.config import Config
from ..events.event_handler import EventHandler
from ..ui.label import Label


class IDE:

    def __init__(self, load_filename: str = None, save_filename: str = None) -> None:
        os.system("cls")

        pygame.init()
        pygame.font.init()

        self.win = pygame.display.set_mode(Config.WINDOW_SIZE, pygame.SRCALPHA)
        pygame.display.set_caption(Config.TITLE)

        self.clock = pygame.time.Clock()

        self.event_handler = EventHandler()
        self.assets = Assets()

        # Graphical
        self.canvas_layer = pygame.Surface(Config.CANVAS_SIZE, pygame.SRCALPHA)

        self.save_filename = save_filename
        self.board = Board(self)
        if load_filename is not None:
            self.board.cells, input_fields = self.load_from_file(load_filename)
            if input_fields is not None:
                self.board.create_input_fields(input_fields)

        self.running = False

        # Settings + Info
        self.help_label = Label(self, "HELP: CTRL + H", 100, 5, self.assets.font24)
        self.run_label = Label(self, "RUN: CTRL + R", 360, 5, self.assets.font24)
        self.kill_label = Label(self, "KILL: CTRL + K", 630, 5, self.assets.font24)
        self.settings_label = Label(self, "SAVE: CTRL + S", 880, 5, self.assets.font24)

        # Excelsis
        self.runner = None
        self.process_running = True
        self.check_for_thread_killed = False

    def run(self) -> None:
        """Runs the app."""

        self.running = True
        while self.running:

            self.update()
            if self.event_handler.quit():
                self.save_to_file(self.save_filename)
                return
            self.render()

            self.clock.tick(Config.FPS)

    def update(self) -> None:
        self.event_handler.update()

        if self.event_handler.quit():
            self.running = False
            self.process_running = False
            return

        if (
            (self.event_handler.keydown(pygame.K_RCTRL)
             or self.event_handler.keydown(pygame.K_LCTRL)) and
            self.event_handler.key_just_pressed() == pygame.K_s
        ):
            self.save_to_file(self.save_filename)

        self.board.update()

        self.check_info_and_settings_input()

        if (
            self.check_for_thread_killed
            and self.runner is not None
            and not self.runner.thread.is_alive()
        ):
            self.runner = EXCELSISRunner(self.board.cells)
            self.process_running = True
            self.runner.run(self.is_running)
            self.check_for_thread_killed = False

    def check_info_and_settings_input(self) -> None:
        if self.event_handler.keydown(pygame.K_RCTRL) or self.event_handler.keydown(pygame.K_LCTRL):
            if self.event_handler.key_just_pressed() == pygame.K_h:
                self.print_help()
            elif self.event_handler.key_just_pressed() == pygame.K_r:
                self.process_running = False
                if self.runner is None:
                    self.runner = EXCELSISRunner(self.board.cells)
                    self.process_running = True
                    self.runner.run(self.is_running)
                else:
                    self.check_for_thread_killed = True
                os.system("cls")
            elif self.event_handler.key_just_pressed() == pygame.K_k:
                if self.runner is None:
                    return
                self.process_running = False
            elif self.event_handler.key_just_pressed() == pygame.K_f and self.event_handler.keydown(pygame.K_LALT):
                os.system("cls")

    def print_help(self) -> None:
        os.system("cls")
        print("HELP".center(50, "-"))

    def render(self) -> None:
        self.win.fill(Config.BOARD_COLOR)
        self.canvas.fill((0, 0, 0))

        self.board.render()

        self.win.blit(self.canvas, (self.win.get_width() - self.canvas.get_width(),
                                    self.win.get_height() - self.canvas.get_height()))

        self.render_info_and_settings()

        pygame.display.update()

    def render_info_and_settings(self) -> None:
        self.help_label.render(canvas=self.win)
        self.run_label.render(canvas=self.win)
        self.kill_label.render(canvas=self.win)
        self.settings_label.render(canvas=self.win)

    @property
    def canvas(self) -> pygame.Surface:
        return self.canvas_layer

    def save_to_file(self, filename: str):
        if filename is None:
            return
        with open(filename, "wb") as file:
            pickle.dump((self.board.cells, list(map(lambda x: (x[0], x[1].code), self.board.cells.items()))), file)

    def load_from_file(self, filename: str):
        with open(filename, "rb") as file:
            try:
                return pickle.load(file)
            except (pickle.UnpicklingError, EOFError):
                return self.board.cells, None

    def is_running(self) -> bool:
        return self.process_running

