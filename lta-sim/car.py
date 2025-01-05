import pygame
import numpy as np


class Car:
    def __init__(self, x: int, y: int, pixels_per_m: int, lanes: np.ndarray) -> None:
        self.image = pygame.image.load("car.png")
        self.wheel_base = 2.9  # Wheelbase
        self.state = np.array([x, y, np.pi / 2, 0.0])
        self.lanes = lanes
        self.pixels_per_m = pixels_per_m

        # Car width in meters (using image height because image is rotated)
        self.width = self.image.get_height() / pixels_per_m

    @property
    def x(self) -> float:
        return self.state[0]

    @property
    def y(self) -> float:
        return self.state[1]

    @property
    def orientation(self) -> float:
        return self.state[2]

    @property
    def steering_angle(self) -> float:
        return self.state[3]

    @staticmethod
    def get_state_var(state: np.ndarray, var: str) -> float:
        idx = ["x", "y", "theta", "v", "phi"].index(var)
        return state[idx]

    def kinematics_model(self, u: np.ndarray) -> np.ndarray:
        A = np.array(
            [
                [np.cos(self.orientation), 0],
                [np.sin(self.orientation), 0],
                [np.tan(self.steering_angle) / self.wheel_base, 0],
                [0, 1],
            ]
        )

        return A @ u

    def integrate_kinematics(
        self, d_state: np.ndarray, dt: float
    ) -> tuple[float, float]:
        half_width = self.width / 2
        self.state += d_state * dt

        # Constrain steering angle to be between -pi/4 and pi/4
        self.state[3] = np.clip(self.state[3], -np.pi / 4, np.pi / 4)

        # return dist in x to left and right lane
        dist = self.lanes - self.x

        try:
            left_dist = dist[1] + half_width
            right_dist = dist[2] - half_width
        except ValueError:
            left_dist = 0.0
            right_dist = 0.0

        return float(-left_dist), float(right_dist)

    def draw(self, screen: pygame.Surface) -> None:
        rotated_image = pygame.transform.rotate(self.image, np.degrees(self.theta))
        rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, rect.topleft)

    def set_velocity(self, v: float) -> None:
        self.v = v
