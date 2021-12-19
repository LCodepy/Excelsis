import pygame

from ..utils.singleton import Singleton


class Assets(metaclass=Singleton):

    def __init__(self) -> None:
        self.font18 = pygame.font.SysFont("consolas", 18)
        self.font24 = pygame.font.SysFont("consolas", 24)
        self.font32 = pygame.font.SysFont("consolas", 32)
        self.font48 = pygame.font.SysFont("consolas", 48)
