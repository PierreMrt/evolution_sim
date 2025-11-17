"""Resources available in the world."""
from dataclasses import dataclass


@dataclass
class Resources:
    food: float = 100.0
    water: float = 100.0
