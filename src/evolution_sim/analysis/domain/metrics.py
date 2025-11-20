"""Data models for analysis metrics."""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class GlobalMetrics:
    """Global simulation metrics collected every 10 frames."""
    
    frame: int
    timestamp: str
    total_population: int
    herbivore_count: int
    carnivore_count: int
    plant_count: int
    avg_energy: float
    min_energy: float
    max_energy: float
    birth_rate: float
    death_rate: float
    avg_age: float
    avg_fitness: float
    avg_neurons: float
    avg_connections: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame conversion."""
        return asdict(self)


@dataclass
class CreatureSnapshot:
    """Individual creature snapshot collected every 50 frames."""
    
    frame: int
    timestamp: str
    creature_id: int
    creature_type: str
    generation: int
    pos_x: float
    pos_y: float
    direction: float
    energy: float
    age: int
    fitness: float
    food_eaten: int
    distance_traveled: float
    neuron_count: int
    connection_count: int
    parent_id: Optional[int]
    children_count: int
    move_speed: float
    direction_change: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame conversion."""
        return asdict(self)


@dataclass
class PlantPosition:
    """Plant position collected every 50 frames."""
    
    frame: int
    timestamp: str
    plant_id: int
    plant_x: float
    plant_y: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame conversion."""
        return asdict(self)
