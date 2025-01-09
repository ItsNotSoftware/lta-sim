import numpy as np


class Controller:
    def __init__(
        self, kp: int, ki: int, kd: int, anti_windup: float, saturation: float
    ) -> None:
        # Gains
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.anti_windup = anti_windup
        self.saturation = saturation

        self.integral = 0
        self.prev_error = 0

        # PID terms (for logging)
        self.P = 0
        self.I = 0
        self.D = 0
        self.u = 0

    def compute_steering(self, target: float, current: float, dt: float) -> float:
        error = current - target
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.anti_windup, self.anti_windup)

        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        self.P = self.kp * error
        self.I = self.ki * self.integral
        self.D = self.kd * derivative

        u = self.P + self.I + self.D
        self.u = u
        return u
