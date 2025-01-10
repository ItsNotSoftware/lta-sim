from ui import UI, Event, PIXELS_PER_METER
from car import Car
from controller import Controller

import numpy as np
import pygame
import socket
import json
import time

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1600
CAR_SPEED = 10  # m/s
SW_TURN_SPEED = np.pi / 4  # rad/s
FPS = 60
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

curve_amplitude = SCREEN_WIDTH // 12 / PIXELS_PER_METER 
curve_frequency = 0.002  

def road_curve(y):
    """Calculate the horizontal offset of the road at a given y-coordinate."""
    return int(curve_amplitude * np.sin(curve_frequency * (y + pygame.time.get_ticks() / 1000 * CAR_SPEED)))

def setup_udp_socket(ip: str, port: int) -> tuple[socket.socket, tuple]:
    """Setup the UDP socket."""
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
            "target": to_serializable(target),
            "car_x": to_serializable(car.x),
            "car_theta": to_serializable(car.orientation),
            "steering_angle": to_serializable(car.steering_angle),
            "car_theta": to_serializable(0),
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


def main() -> None:
    ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT, CAR_SPEED, FPS)
    lanes = np.array(ui.lanes) / PIXELS_PER_METER
    center_line = (lanes[2] + lanes[1]) / 2
    car = Car(
        SCREEN_WIDTH / (2 * PIXELS_PER_METER),
        SCREEN_HEIGHT / (2 * PIXELS_PER_METER),
        PIXELS_PER_METER,
        lanes,
    )
    controller = Controller(0.2, 0.09, 0.1, np.pi / 3, np.pi / 3)

    sock, address = setup_udp_socket(UDP_IP, UDP_PORT)
    pygame.init()
    prev_time = time.time()
    tick_count = 0

    while True:
        center_line = (ui.current_lanes[2] + ui.current_lanes[1]) / 2 / PIXELS_PER_METER
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
            case Event.NO_EVENT:
                u = np.array([CAR_SPEED, 0]).astype(np.float64)
        
        ui.draw(car)

        timestamp = time.time()
        dt = timestamp - prev_time
        prev_time = timestamp

        # Disable controller if player is steering for 1/8s  
        if tick_count > FPS / 8:
            # PID to get target steering angle
            target_phi = controller.compute_steering(car.x, center_line + road_curve(car.y), dt)
            
            # Feedforward to calculate target turn rate to reach target steering angleS
            u[1] = (target_phi - car.steering_angle) / dt

        # Calculate car dynamics
        d_state = car.kinematics_model(u) 
        left_dist, right_dist = car.integrate_kinematics(d_state, dt)

        car.lanes = ui.current_lanes / PIXELS_PER_METER

        publish_car_state(
            sock,
            address,
            timestamp * 1000,
            left_dist,
            right_dist,
            CAR_SPEED,
            u[1],
            center_line,
            car,
            controller,
        )

        tick_count += 1

    pygame.quit()
    sock.close()

if __name__ == "__main__":
    main()
