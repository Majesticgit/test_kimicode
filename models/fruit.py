"""Shared fruit enumeration used across the application."""
from enum import Enum


class FruitType(str, Enum):
    """Supported fruit categories."""

    WHITE_PEACH = "white_peach"
    RED_APPLE = "red_apple"
    WATERMELON = "watermelon"
