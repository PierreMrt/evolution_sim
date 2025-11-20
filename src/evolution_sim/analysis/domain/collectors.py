"""Pure functions to extract data from environment."""

import logging
from typing import List
from datetime import datetime
from evolution_sim.analysis.domain.metrics import (
    GlobalMetrics,
    CreatureSnapshot,
    PlantPosition
)

logger = logging.getLogger(__name__)


def collect_global_metrics(frame: int, environment) -> GlobalMetrics:
    """
    Collect global simulation metrics.
    
    Args:
        frame: Current simulation frame
        environment: Environment instance
        
    Returns:
        GlobalMetrics instance with aggregated statistics
    """
    try:
        alive_creatures = [c for c in environment.creatures if c.alive]
        herbivores = [c for c in alive_creatures if c.creature_type == 'herbivore']
        carnivores = [c for c in alive_creatures if c.creature_type == 'carnivore']
        
        # Calculate averages
        if alive_creatures:
            avg_energy = sum(c.energy for c in alive_creatures) / len(alive_creatures)
            min_energy = min(c.energy for c in alive_creatures)
            max_energy = max(c.energy for c in alive_creatures)
            avg_age = sum(c.age for c in alive_creatures) / len(alive_creatures)
            avg_fitness = sum(c.genome.fitness for c in alive_creatures) / len(alive_creatures)
            avg_neurons = sum(len(c.brain.neurons) for c in alive_creatures) / len(alive_creatures)
            avg_connections = sum(len(c.brain.connections) for c in alive_creatures) / len(alive_creatures)
        else:
            avg_energy = min_energy = max_energy = 0.0
            avg_age = avg_fitness = avg_neurons = avg_connections = 0.0
        
        # Birth and death rates (placeholder - would need tracking)
        birth_rate = 0.0  # Can be calculated from tracker
        death_rate = 0.0  # Can be calculated from tracker
        
        return GlobalMetrics(
            frame=frame,
            timestamp=datetime.now().isoformat(),
            total_population=len(alive_creatures),
            herbivore_count=len(herbivores),
            carnivore_count=len(carnivores),
            plant_count=len(environment.plants),
            avg_energy=round(avg_energy, 2),
            min_energy=round(min_energy, 2),
            max_energy=round(max_energy, 2),
            birth_rate=birth_rate,
            death_rate=death_rate,
            avg_age=round(avg_age, 2),
            avg_fitness=round(avg_fitness, 2),
            avg_neurons=round(avg_neurons, 2),
            avg_connections=round(avg_connections, 2)
        )
    except Exception as e:
        logger.error(f"Error collecting global metrics: {e}")
        raise


def collect_creature_snapshots(frame: int, environment) -> List[CreatureSnapshot]:
    """
    Collect snapshots of all living creatures.
    
    Args:
        frame: Current simulation frame
        environment: Environment instance
        
    Returns:
        List of CreatureSnapshot instances
    """
    try:
        snapshots = []
        timestamp = datetime.now().isoformat()
        
        for creature in environment.creatures:
            if not creature.alive:
                continue
                
            # Calculate move speed (magnitude of last movement)
            move_speed = 0.0  # Would need to track velocity
            direction_change = 0.0  # Would need to track previous direction
            
            snapshot = CreatureSnapshot(
                frame=frame,
                timestamp=timestamp,
                creature_id=creature.id,
                creature_type=creature.creature_type,
                generation=creature.generation,
                pos_x=round(creature.x, 2),
                pos_y=round(creature.y, 2),
                direction=round(creature.direction, 4),
                energy=round(creature.energy, 2),
                age=creature.age,
                fitness=round(creature.genome.fitness, 2),
                food_eaten=creature.food_eaten,
                distance_traveled=round(creature.distance_traveled, 2),
                neuron_count=len(creature.brain.neurons),
                connection_count=len(creature.brain.connections),
                parent_id=creature.parent_id,
                children_count=creature.children_count,
                move_speed=round(move_speed, 2),
                direction_change=round(direction_change, 4)
            )
            snapshots.append(snapshot)
        
        return snapshots
    except Exception as e:
        logger.error(f"Error collecting creature snapshots: {e}")
        raise


def collect_plant_positions(frame: int, environment) -> List[PlantPosition]:
    """
    Collect positions of all plants.
    
    Args:
        frame: Current simulation frame
        environment: Environment instance
        
    Returns:
        List of PlantPosition instances
    """
    try:
        positions = []
        timestamp = datetime.now().isoformat()
        
        for plant_id, plant in enumerate(environment.plants):
            # plant is stored as a tuple (x, y)
            position = PlantPosition(
                frame=frame,
                timestamp=timestamp,
                plant_id=plant_id,
                plant_x=round(plant[0], 2),
                plant_y=round(plant[1], 2)
            )
            positions.append(position)
        
        return positions
    except Exception as e:
        logger.error(f"Error collecting plant positions: {e}")
        raise
