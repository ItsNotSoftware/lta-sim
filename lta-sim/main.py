from ui import UI, Event, PIXELS_PER_METER
from car import Car

import numpy as np
import pygame
import socket
import json 

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1600
CAR_SPEED = 12  # m/s
SW_TURN_SPEED = np.pi / 4  # rad/s
FPS = 60
DT = 1 / FPS
UDP_IP = "127.0.0.1"  # Replace with PlotJuggler's IP if remote
UDP_PORT = 5005


def setup_udp_socket(ip: str, port: int):
    """Setup the UDP socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (ip, port)
    return sock, address


def publish_car_state(sock: socket.socket, address: tuple, timestamp: float, left_dist: float, right_dist: float, car_speed: float, turn_rate: float) -> None:
    """Publish the car's state in JSON format."""
    def to_serializable(value):
        """Convert a value to a JSON-serializable Python type."""
        if isinstance(value, (np.integer, np.floating)):
            return value.item()  # Convert numpy scalar to Python type
        elif isinstance(value, np.ndarray):
            return value.tolist()  # Convert numpy array to Python list
        return value  # Return native Python types as-is

    # Convert all values to JSON-serializable types
    data = {
        "timestamp": to_serializable(timestamp),
        "signals": {
            "left_distance": to_serializable(left_dist),
            "right_distance": to_serializable(right_dist),
            "car_speed": to_serializable(car_speed),
            "turn_rate": to_serializable(turn_rate),
        },
    }

    # Send JSON string via UDP
    json_data = json.dumps(data)
    sock.sendto(json_data.encode(), address)


def main() -> None:
    # UI and Car setup
    ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT, CAR_SPEED, FPS)
    car = Car(
        SCREEN_WIDTH / (2 * PIXELS_PER_METER),
        SCREEN_HEIGHT / (2 * PIXELS_PER_METER),
        PIXELS_PER_METER,
        np.array(ui.lanes) / PIXELS_PER_METER,
    )

    sock, address = setup_udp_socket(UDP_IP, UDP_PORT)
    pygame.init()

    try:
        while True:
            event = ui.event_handler()

            match event:
                case Event.QUIT:
                    break
                case Event.SW_LEFT:
                    u = np.array([CAR_SPEED, SW_TURN_SPEED])
                case Event.SW_RIGHT:
                    u = np.array([CAR_SPEED, -SW_TURN_SPEED])
                case Event.NO_EVENT:
                    u = np.array([CAR_SPEED, 0])

            # Calculate car dynamics
            d_state = car.kinematics_model(u)
            left_dist, right_dist = car.integrate_kinematics(d_state, DT)

            timestamp = pygame.time.get_ticks() / 1000.0  # Convert ms to seconds
            publish_car_state(sock, address, timestamp, left_dist, right_dist, CAR_SPEED, u[1])

            # Draw UI
            ui.draw(car)

    finally:
        pygame.quit()
        sock.close()


if __name__ == "__main__":
    main()
