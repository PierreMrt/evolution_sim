"""Creature implementation with neural network control."""
import math
import random
from typing import List, TYPE_CHECKING
from .genome import Genome
from .neural_network import NeuralNetwork
from ..config import config

if TYPE_CHECKING:
    from ..environment.world import Environment


class Creature:
    """Individual creature in the simulation."""
    
    _id_counter = 0
    
    def __init__(self, x: float, y: float, genome: Genome, brain=None, parent_id=None, generation=0):
        """Initialize a creature."""
        self.id = Creature._id_counter
        Creature._id_counter += 1
        
        self.x = x
        self.y = y
        self.genome = genome
        self.creature_type = genome.creature_type
        
        self.parent_id = parent_id
        self.generation = generation
        self.birth_time = 0 
        self.death_time = None
        self.children_count = 0
        
        max_energy = config.get('creatures.max_energy')
        
        # CARNIVORES START WITH MORE ENERGY
        if self.creature_type == 'carnivore':
            self.energy = max_energy * 0.7  # 70% energy (was 50%)
        else:
            self.energy = max_energy * 0.5  # 50% energy
        
        self.age = 0
        self.alive = True
        
        # Random initial direction
        self.direction = random.uniform(0, 2 * math.pi)
        
        # CARNIVORES ARE LARGER AND FASTER
        if self.creature_type == 'herbivore':
            self.radius = config.get('creatures.herbivore_radius')
            self.speed_multiplier = 1.0  # Normal speed
        else:
            self.radius = config.get('creatures.carnivore_radius')
            self.speed_multiplier = 1.2  
        
        self.food_eaten = 0
        self.distance_traveled = 0.0
        self.eat_cooldown = 0
        
        # Use genome's network
        self.brain = genome.network
        
    def get_inputs(self, environment: 'Environment') -> List[float]:
        """
        Generate neural network inputs from environment.
        
        Args:
            environment: The simulation environment
            
        Returns:
            List of input values for the neural network
        """
        max_energy = config.get('creatures.max_energy')
        inputs = [1.0]  # Bias
        inputs.append(self.energy / max_energy)
        
        # Find nearest food using spatial grid when available
        if environment is not None:
            if self.creature_type == 'herbivore':
                nearest_food = self._find_nearest(None, entity_type='plant', environment=environment)
            else:
                nearest_food = self._find_nearest(None, entity_type='herbivore', environment=environment)
        else:
            nearest_food = self._find_nearest(
                environment.plants if self.creature_type == 'herbivore' 
                else environment.get_prey(self)
            )
        inputs.extend(nearest_food)
        
        # Find nearest threat
        if environment is not None:
            # For herbivores, predators are carnivores; for carnivores assume carnivore threats (could be none)
            threat_type = 'carnivore' if self.creature_type == 'herbivore' else 'carnivore'
            nearest_threat = self._find_nearest(None, entity_type=threat_type, environment=environment)
        else:
            nearest_threat = self._find_nearest(environment.get_predators(self))
        inputs.extend(nearest_threat)
        
        # Find nearest prey (for carnivores)
        if self.creature_type == 'carnivore':
            nearest_prey = self._find_nearest(None, entity_type='herbivore', environment=environment)
            inputs.extend(nearest_prey)
        else:
            inputs.extend([0, 0])
        
        input_neurons = config.get('neural_network.input_neurons')
        return inputs[:input_neurons]
    

    def _find_nearest(self, entities=None, entity_type: str = None, environment: 'Environment' = None):
        """Find nearest entity from a list or from the environment spatial grid and return normalized direction.

        Args:
            entities: optional iterable of entities (list of (x,y) or Creature)
            entity_type: when provided with environment, query this type from the grid ('plant','herbivore','carnivore')
            environment: Environment instance with spatial_grid
        """
        # Acquire candidates
        candidates = None
        if environment is not None and entity_type is not None:
            # Use spatial grid if available
            try:
                candidates = environment.spatial_grid.query_neighborhood(self.x, self.y, entity_type)
            except Exception:
                candidates = []
        elif entities is not None:
            candidates = entities

        if not candidates:
            return [0.0, 0.0]

        nearest = None
        min_dist = float('inf')
        for entity in candidates:
            if hasattr(entity, 'x'):
                ex, ey = entity.x, entity.y
            else:
                ex, ey = entity[0], entity[1]

            dist = math.hypot(self.x - ex, self.y - ey)
            if dist < min_dist:
                min_dist = dist
                nearest = (ex, ey)

        if nearest is None:
            return [0.0, 0.0]

        dx = nearest[0] - self.x
        dy = nearest[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            return [dx / dist, dy / dist]
        return [0.0, 0.0]
    

    def think_and_act(self, environment):
        """Process inputs through neural network and take action"""
        inputs = self.get_inputs(environment)
        outputs = self.brain.forward(inputs)
        
        # Interpret outputs
        turn = outputs[0] * 0.2
        base_speed = outputs[1] * 2.0
        
        # Apply carnivore speed multiplier
        speed = base_speed * self.speed_multiplier
        
        # Update direction and position
        self.direction += turn
        dx = math.cos(self.direction) * speed
        dy = math.sin(self.direction) * speed
        
        self.x += dx
        self.y += dy
        
        # Wrap around screen edges
        world_width = config.get('world.width')
        world_height = config.get('world.height')
        self.x = self.x % world_width
        self.y = self.y % world_height
        
        # CARNIVORES PAY LESS ENERGY FOR MOVEMENT (efficient hunters)
        if self.creature_type == 'carnivore':
            self.energy -= abs(speed) * 0.02 + abs(turn) * 0.015
        else:
            self.energy -= abs(speed) * 0.03 + abs(turn) * 0.02
        
        # Try to eat
        self.try_eat(environment)

    
    def _move(self, dx: float, dy: float) -> None:
        """Move the creature and consume energy."""
        world_width = config.get('world.width')
        world_height = config.get('world.height')
        move_cost = config.get('creatures.move_energy_cost')
        
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy
        
        # Keep in bounds
        self.x = max(self.radius, min(world_width - self.radius, self.x))
        self.y = max(self.radius, min(world_height - self.radius, self.y))
        
        # Energy cost
        distance = math.sqrt((self.x - old_x)**2 + (self.y - old_y)**2)
        self.distance_traveled += distance
        self.energy -= move_cost * distance
    
    def try_eat(self, environment: 'Environment') -> None:
        """
        Attempt to eat food or attack prey.
        
        Args:
            environment: The simulation environment
        """
        if self.creature_type == 'herbivore':
            self._eat_plants(environment)
        else:
            self._attack_prey(environment)
    
    def _eat_plants(self, environment: 'Environment') -> None:
        """Eat nearby plants."""
        plant_energy = config.get('world.plant_energy')
        max_energy = config.get('creatures.max_energy')
        # Prefer querying local cell for plants if grid available
        if hasattr(environment, 'spatial_grid'):
            candidates = environment.spatial_grid.query_local_cell(self.x, self.y, 'plant')
        else:
            candidates = environment.plants[:]

        for plant in list(candidates):
            if hasattr(plant, 'x'):
                px, py = plant.x, plant.y
            else:
                px, py = plant[0], plant[1]
            dist = math.hypot(px - self.x, py - self.y)
            if dist < self.radius + 5:
                # Remove from environment plant list if present
                try:
                    environment.plants.remove((px, py))
                except Exception:
                    # maybe plant is an object; try to remove by identity
                    try:
                        environment.plants.remove(plant)
                    except Exception:
                        pass
                self.energy = min(max_energy, self.energy + plant_energy)
                self.food_eaten += 1
                break
    
    def _attack_prey(self, environment: 'Environment') -> None:
        """Attack nearby herbivores."""
        max_energy = config.get('creatures.max_energy')
        # Query local cell for potential prey when possible
        if hasattr(environment, 'spatial_grid'):
            candidates = environment.spatial_grid.query_local_cell(self.x, self.y, 'herbivore')
        else:
            candidates = [c for c in environment.creatures if c.creature_type == 'herbivore']

        for creature in list(candidates):
            if not getattr(creature, 'alive', True):
                continue
            dist = math.hypot(creature.x - self.x, creature.y - self.y)
            if dist < self.radius + creature.radius:
                creature.alive = False
                self.energy = min(max_energy, self.energy + 50)
                self.food_eaten += 1
                break
    
    def update(self) -> None:
        """Update creature state."""
        self.age += 1
        self.energy -= 0.03  # Base metabolism
        
        if self.energy <= 0:
            self.alive = False
        
        # Calculate fitness
        self.genome.fitness = self.food_eaten * 10 + self.age * 0.1
    
    def can_reproduce(self) -> bool:
        """
        Check if creature can reproduce.
        
        Returns:
            True if creature has enough energy and age
        """
        threshold = config.get('creatures.reproduction_energy_threshold')
        return self.energy > threshold and self.age > 100
    
    def reproduce(self) -> 'Creature':
        """
        Create offspring with mutations.
        
        Returns:
            New Creature instance (offspring)
        """
        repro_cost = config.get('creatures.reproduction_cost')
        self.energy -= repro_cost
        
        offspring_genome = self.genome.copy()
        offspring_genome.mutate()
        
        # Track offspring
        self.children_count += 1
        
        # Spawn near parent
        offset_x = random.uniform(-30, 30)
        offset_y = random.uniform(-30, 30)
        
        # Pass generation and parent info
        return Creature(
            self.x + offset_x, 
            self.y + offset_y, 
            offspring_genome,
            parent_id=self.id,
            generation=self.generation + 1
        )
