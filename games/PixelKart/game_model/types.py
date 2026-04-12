
from enum import StrEnum

class Action(StrEnum):
    """Actions available to the kart each turn."""

    ACCELERATE = "accelerate"
    BRAKE = "brake"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    WAIT = "wait"

class Pixel(StrEnum):
    """Track pixel supported by the model."""

    ROAD = "road"
    GRASS = "grass"
    WALL = "wall"
    START = "start"

Position = tuple[int, int]
RawPixel = str | int | Pixel