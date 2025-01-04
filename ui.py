import pygame
import numpy as np
from car import Car
from enum import Enum, auto


class Event(Enum):
    QUIT = auto()
    SW_LEFT = auto()
    SW_RIGHT = auto()
    NO_EVENT = auto()


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRASS = (0, 180, 0)
    ROAD = (128, 128, 128)


class UI:
    def __init__(self, width: int, height: int, fps: int) -> None:
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        self.fps = fps

    def event_handler(self) -> Event:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Event.QUIT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return Event.QUIT

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return Event.SW_LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return Event.SW_RIGHT

        return Event.NO_EVENT

    def _draw_img(
        self, img: pygame.Surface, x: int, y: int, orientation: float
    ) -> None:
        rotated_img = pygame.transform.rotate(img, -np.degrees(orientation))
        rect = rotated_img.get_rect(center=(x, y))
        self.screen.blit(rotated_img, rect.topleft)

    def draw_road(self) -> None:
        # Draw grass on both sides
        grass_width = self.width // 6
        pygame.draw.rect(self.screen, Color.GRASS, (0, 0, grass_width, self.height))
        pygame.draw.rect(
            self.screen,
            Color.GRASS,
            (self.width - grass_width, 0, grass_width, self.height),
        )

        # Draw road
        road_width = self.width - 2 * grass_width
        pygame.draw.rect(
            self.screen, Color.ROAD, (grass_width, 0, road_width, self.height)
        )

        # Draw lane lines
        lane_width = road_width // 3
        for i in range(1, 3):
            x = grass_width + i * lane_width
            pygame.draw.line(self.screen, Color.WHITE, (x, 0), (x, self.height), 5)

    def draw(self, car: Car) -> None:
        self.draw_road()
        self._draw_img(car.image, car.x, self.height // 2, -car.orientation)

        pygame.display.flip()
        self.clock.tick(self.fps)
