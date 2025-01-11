import pygame
import numpy as np


class Car:
    """ A class to represent a car in the simulation using bycicle model. """
    def __init__(self, x: int, y: int, pixels_per_m: int, lanes: np.ndarray) -> None:
        """
        Initialize the car.

        Args:
            x: The x-coordinate of the car.
            y: The y-coordinate of the car.
            pixels_per_m: The number of ui pixels per simulation meter.
            lanes: The x-coordinates of the lanes.
        """
        self.image = pygame.image.load("car.png")
        self.wheel_base = 2.5  # Wheelbase
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

    def kinematics_model(self, u: np.ndarray) -> np.ndarray:
        """
        Compute the state derivative of the car using bycle model.

        Args:
            u: The control input to the car [v, ws].
        
        Returns:
            The state derivative of the car.            
        """

        A = np.array(
            [
                [np.cos(self.orientation), 0],
                [np.sin(self.orientation), 0],
                [np.tan(self.steering_angle) / self.wheel_base, 0],
                [0, 1],
            ]
        )

        return A @ u

    def integrate_kinematics(self, d_state: np.ndarray, dt: float) -> tuple[float, float]:
        """
        Integrate the kinematics of the car.

        Args:
            d_state: The state derivative of the car.
            dt: The time step.

        Returns:
            A tuple containing the distance to the left and right lanes.
        """  
        half_width = self.width / 2
        self.state += d_state * dt

        # Constrain steering angle to be between -pi/3 and pi/3
        self.state[3] = np.clip(self.state[3], -np.pi / 3, np.pi / 3)

        # return dist in x to left and right lane
        dist = self.lanes - self.x

        try:
            left_dist = dist[1] + half_width
            right_dist = dist[2] - half_width
        except ValueError:
            left_dist = 0.0
            right_dist = 0.0

        return float(-left_dist), float(right_dist)
