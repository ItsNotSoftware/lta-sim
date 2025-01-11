import pygame
import numpy as np
from car import Car
from enum import Enum, auto

PIXELS_PER_METER = 60
LANE_WIDTH = 6
DASH_LENGTH = 70
DASH_GAP = 80


class Event(Enum):
    QUIT = auto()
    SW_LEFT = auto()
    SW_RIGHT = auto()
    LOCK = auto()
    NO_EVENT = auto()


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRASS = (0, 180, 0)
    ROAD = (128, 128, 128)


class UI:
    def __init__(
        self,
        width: int,
        height: int,
        speed: int,
        fps: int,
        amplitude: float,
        freq: float,
    ) -> None:
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        self.speed = speed * PIXELS_PER_METER
        self.fps = fps
        self.lanes = self.init_lanes(width)
        self.current_lanes = self.lanes
        self.dash_offset = 0
        self.amplitude = amplitude
        self.freq = freq

    @staticmethod
    def init_lanes(width) -> np.ndarray:
        grass_width = width // 6
        road_width = width - 2 * grass_width
        lane_width = road_width // 3
        lanes = [grass_width + i * lane_width for i in range(4)]
        return np.array(lanes)

    def event_handler(self) -> Event:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return Event.QUIT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return Event.QUIT
                if event.key == pygame.K_l:
                    return Event.LOCK

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

    def draw_road(self, theta: float, time: float, car_y: int) -> None:
        # Draw grass on both sides
        grass_width = self.width // 6
        pygame.draw.rect(self.screen, Color.ROAD, (0, 0, grass_width, self.height))
        pygame.draw.rect(
            self.screen,
            Color.ROAD,
            (self.width - grass_width, 0, grass_width, self.height),
        )

        # Draw road
        road_width = self.width - 2 * grass_width
        pygame.draw.rect(
            self.screen, Color.ROAD, (grass_width, 0, road_width, self.height)
        )

        # Update dash offset based on speed and fps
        self.dash_offset += self.speed * np.sin(theta) / self.fps
        total_dash_height = DASH_LENGTH + DASH_GAP

        # Loop offset to keep it wiFthin one dash cycle
        self.dash_offset %= total_dash_height

        def road_curve(y):
            """Calculate the horizontal offset of the road at a given y-coordinate."""
            return int(self.amplitude * np.sin(self.freq * (y + time * self.speed)))

        # Draw lane dividers (dashed lines) with sinusoidal curves
        for x in self.lanes[1:-1]:
            for y in range(-int(total_dash_height), self.height, total_dash_height):
                dash_y_start = y + self.dash_offset
                dash_y_end = dash_y_start + DASH_LENGTH
                if dash_y_start < self.height:
                    pygame.draw.line(
                        self.screen,
                        Color.WHITE,
                        (x + road_curve(dash_y_start), dash_y_start),
                        (x + road_curve(dash_y_end), dash_y_end),
                        LANE_WIDTH,
                    )

        # Draw lane boundaries with sinusoidal curves
        for y in range(0, self.height):
            if y % 2 == 0:  # Optimize drawing by skipping some pixels
                left_x = self.lanes[0] + road_curve(y)
                right_x = self.lanes[-1] + road_curve(y)
                pygame.draw.line(
                    self.screen,
                    Color.WHITE,
                    (left_x, y),
                    (left_x + 1, y),
                    LANE_WIDTH,
                )
                pygame.draw.line(
                    self.screen,
                    Color.WHITE,
                    (right_x, y),
                    (right_x + 1, y),
                    LANE_WIDTH,
                )
        self.current_lanes = self.lanes + road_curve(car_y)

    def draw(self, car: Car) -> None:
        current_time = pygame.time.get_ticks() / 1000  # Get time in seconds
        self.draw_road(car.orientation, current_time, self.height // 1.5)

        self._draw_img(
            car.image, car.x * PIXELS_PER_METER, self.height // 1.5, -car.orientation
        )

        pygame.display.flip()
        self.clock.tick(self.fps)
