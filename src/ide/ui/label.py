from typing import Tuple, Optional

import pygame


class Label:

    def __init__(self, app, text: str, x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int] = (0, 0, 0),
                 width: int = -1, centerx: bool = True, centery: bool = True, max_width: int = 100, max_height: int = 60) -> None:
        self.app = app
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.width = width
        self.centerx = centerx
        self.centery = centery
        self.max_width = max_width
        self.max_height = max_height

        self.height = 0
        self.y_gap = 3

        self.lines = [""]

        self.update_text(self.text)

    def render(self, canvas: Optional[pygame.Surface] = None) -> None:
        for i, line in enumerate(self.lines):
            rend = Label.text(self.font, line, color=self.color)
            x = self.x - (rend.get_width() // 2 if self.centerx else 0)
            y = self.y - ((len(self.lines) - 1) * (self.y_gap + self.height) // 2 if self.centery else 0) + self.y_gap * i + self.height * i
            (canvas or self.app.canvas).blit(rend, (x, y))

    def render_rect(self, cx: int, cy: int, w: int, h: int, canvas: Optional[pygame.Surface] = None) -> None:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for i, line in enumerate(self.lines):
            rend = Label.text(self.font, line, color=self.color)
            x = self.max_width // 2 - (rend.get_width() // 2 if self.centerx else 0)
            y = self.max_height // 2 + self.y_gap * i + self.height * i - ((len(self.lines) - 1) * (self.y_gap + self.height) // 2 if self.centery else 0)
            surf.blit(rend, (x, y))
        (canvas or self.app.canvas).blit(surf, (cx, cy))

    def update_text(self, text) -> None:
        self.text = text

        self.lines = [""]

        words = self.text.split(" ")

        self.height = Label.text(self.font, "L").get_height()

        i = 0
        for w in words:
            if Label.text(self.font, self.lines[i] + " " + w).get_width() <= self.width or self.width == -1:
                self.lines[i] += " " + w
            else:
                self.lines.append(w)
                i += 1

    def get_end_pos(self) -> Tuple[int, int]:
        return Label.text(self.font, self.lines[-1].replace(" ", "L"), color=self.color).get_width() // 2 + self.x, \
               self.y + self.y_gap * (len(self.lines) - 1) + self.height * (len(self.lines) - 1) \
               - ((len(self.lines) - 1) * (self.y_gap + self.height) // 2 if self.centery else 0)

    @staticmethod
    def text(font: pygame.font.Font, text: str, bold: bool = False,
             color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
        return font.render(text, bold, color)
