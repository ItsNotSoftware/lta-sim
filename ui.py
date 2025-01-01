import pygame
import sys


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRASS = (0, 180, 0)
    ROAD = (128, 128, 128)


class UI:
    def __init__(self, width: int, height: int) -> None:
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        self.car = pygame.transform.rotate(pygame.image.load("car.png"), -90)
        self.width = width
        self.height = height

    def event_handler(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            print("Left")
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            print("Right")

    def _draw_img(self, img: pygame.Surface, x: int, y: int) -> None:
        self.screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))

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

    def draw(self) -> None:
        self.screen.fill(Color.WHITE)

        self.draw_road()
        self._draw_img(self.car, self.width // 2, self.height // 1.5)  

        pygame.display.flip()
        self.clock.tick(60)
