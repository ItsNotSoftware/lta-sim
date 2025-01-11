class Controller:
    """PID controller for steering angle control."""

    def __init__(self, kp: int, ki: int, kd: int) -> None:
        """
        Initialize the controller.

        Args:
            kp: The proportional gain.
            ki: The integral gain.
            kd: The derivative gain.
        """
        # Gains
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.integral = 0
        self.prev_error = 0

        # PID terms (for logging)
        self.P = 0
        self.I = 0
        self.D = 0
        self.u = 0

    def compute_steering(self, target: float, current: float, dt: float) -> float:
        # Calculate error
        error = target - current

        # Compute integral term with anti-windup
        self.integral += error * dt

        # Compute derivative term
        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        # Compute PID terms
        self.P = self.kp * error
        self.I = self.ki * self.integral
        self.D = self.kd * derivative

        # Compute raw control signal
        u = self.P + self.I + self.D

        self.u = u

        return u
