from ui import UI, Event, PIXELS_PER_METER
from car import Car
from controller import Controller

import numpy as np
import pygame
import time
import socket
import json
import sys

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1600
CAR_SPEED = 15  # m/s
SW_TURN_SPEED = np.pi / 4  # rad/s
FPS = 60
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
DT = 1 / FPS


def setup_plotjuggler_socket(ip: str, port: int) -> tuple[socket.socket, tuple]:
    """
    Set up a UDP socket to send data to PlotJuggler(https://plotjuggler.io/).

    Args:
        ip: The IP address to send data to.
        port: The port to send data to.

    Returns:
        A tuple containing the socket and address.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (ip, port)
    return sock, address


def publish_car_state(
    sock: socket.socket,
    address: tuple,
    timestamp: float,
    left_dist: float,
    right_dist: float,
    car_speed: float,
    turn_rate: float,
    target: float,
    car: Car,
    controller: Controller,
) -> None:
    """
    Publish the car state to PlotJuggler.

    Args:
        sock: The socket to send data.
        address: The address to send data to.
        timestamp: The timestamp of the data.
        left_dist: The distance to the left lane.
        right_dist: The distance to the right lane.
        car_speed: The speed of the car.
        turn_rate: The turn rate of the car.
        target: The target steering angle.
        car: The car object.
        controller: The controller object.
    """

    def to_serializable(value: any) -> any:
        """Convert a value to a JSON-serializable Python type."""
        if isinstance(value, (np.integer, np.floating)):
            return value.item()
        elif isinstance(value, np.ndarray):
            return value.tolist()
        return value

    # Convert all values to JSON-serializable types
    data = {
        "timestamp": to_serializable(timestamp),
        "signals": {
            "left_distance": to_serializable(left_dist),
            "right_distance": to_serializable(right_dist),
            "car_speed": to_serializable(car_speed),
            "turn_rate": to_serializable(turn_rate),
            "target": to_serializable(target),
            "car_x": to_serializable(car.x),
            "car_theta": to_serializable(car.orientation),
            "steering_angle": to_serializable(car.steering_angle),
            "controller": {
                "P": to_serializable(controller.P),
                "I": to_serializable(controller.I),
                "D": to_serializable(controller.D),
                "error": to_serializable(controller.prev_error),
                "integral": to_serializable(controller.integral),
                "u": to_serializable(controller.u),
            },
        },
    }

    # Send JSON string via UDP
    json_data = json.dumps(data)
    sock.sendto(json_data.encode(), address)


def process_cli_args() -> tuple[float, float]:
    """
    Process command line arguments.

    Returns:
        A tuple containing the amplitude and frequency of the road sine-wave.
    """
    if len(sys.argv) == 3:
        return float(sys.argv[1]), float(sys.argv[2])
    else:
        return 0.0, 0.0


def main() -> None:
    """Main function to run the simulation."""
    # Init variables
    amplitude, freq = process_cli_args()
    ui = UI(
        SCREEN_WIDTH, SCREEN_HEIGHT, CAR_SPEED, FPS, amplitude * PIXELS_PER_METER, freq
    )
    lanes = np.array(ui.lanes) / PIXELS_PER_METER
    center_line = (lanes[2] + lanes[1]) / 2
    car = Car(
        SCREEN_WIDTH / (2 * PIXELS_PER_METER),
        SCREEN_HEIGHT / (2 * PIXELS_PER_METER),
        PIXELS_PER_METER,
        lanes,
    )
    controller = Controller(
        0.2,
        0.09,
        0.1,
    )  # PID controller
    sock, address = setup_plotjuggler_socket(UDP_IP, UDP_PORT)
    pygame.init()

    controller_enabled = True
    tick_count = 0

    # Simulation loop
    while True:
        # Compute center line for car to follow
        center_line = (ui.current_lanes[2] + ui.current_lanes[1]) / 2 / PIXELS_PER_METER

        # Process user input
        event = ui.event_handler()
        match event:
            case Event.QUIT:
                break
            case Event.SW_LEFT:
                u = np.array([CAR_SPEED, SW_TURN_SPEED]).astype(np.float64)
                tick_count = 0
            case Event.SW_RIGHT:
                u = np.array([CAR_SPEED, -SW_TURN_SPEED]).astype(np.float64)
                tick_count = 0
            case Event.TOGGLE_CONTROL:
                controller_enabled = not controller_enabled
                car.state[3] = 0.0  # Reset steering angle
            case Event.NO_EVENT:
                u = np.array([CAR_SPEED, 0]).astype(np.float64)

        # Disable controller if player is steering for 1/8s
        if tick_count > FPS / 8 and controller_enabled:
            # PID to get target steering angle
            target_phi = controller.compute_steering(car.x, center_line, DT)

            # Feedforward to calculate target turn rate to reach target steering angle
            u[1] = (target_phi - car.steering_angle) / DT

        # Calculate car dynamics
        d_state = car.kinematics_model(u)
        left_dist, right_dist = car.integrate_kinematics(d_state, DT)

        car.lanes = ui.current_lanes / PIXELS_PER_METER

        # Publish car state to PlotJuggler
        publish_car_state(
            sock,
            address,
            time.time() * 1000,
            left_dist,
            right_dist,
            CAR_SPEED,
            u[1],
            center_line,
            car,
            controller,
        )

        # Update UI
        ui.draw(car)
        tick_count += 1

    pygame.quit()
    sock.close()


if __name__ == "__main__":
    main()
