from ui import UI, Event
from car import Car
import numpy as np
import pygame

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 1600

CAR_SPEED = 330 
SW_TURN_SPEED = 0.03 
FPS = 60
DT = 1 / FPS


def main() -> None:
    ui = UI(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
    car = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.init()

    # Initialize u outside the loop to persist across iterations
    u = np.array([CAR_SPEED, 0])  # Persistent control input [v, ws]

    while True:
        event = ui.event_handler()

        # Check for events (keyboard input or quit)
        match event:
            case Event.QUIT:
                break
            case Event.SW_LEFT:
                print("SW_LEFT")
                u = np.array([CAR_SPEED, SW_TURN_SPEED])  # Turn left
            case Event.SW_RIGHT:
                print("SW_RIGHT")
                u = np.array([CAR_SPEED, -SW_TURN_SPEED])  # Turn left
            case Event.NO_EVENT:
                u = np.array([CAR_SPEED, -car.steering_angle])  # Go straight

        # Debug: Print the control input to see the changes
        print("Control input u:", u)

        # Update car state
        d_state = car.kinematics_model(u)
        car.integrate_kinematics(d_state, DT)

        # Draw updated state
        ui.draw(car)

    pygame.quit()


if __name__ == "__main__":
    main()

