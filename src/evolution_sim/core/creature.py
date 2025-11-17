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
        """
        Initialize a creature.
        
        Args:
            x: Initial x position
            y: Initial y position
            genome: Genetic information
            brain: Optional pre-built brain
            parent_id: ID of parent creature
            generation: Generation number
        """
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
        self.energy = max_energy * 0.5
        self.age = 0
        self.alive = True
        self.direction = random.uniform(0, 2 * math.pi)
        
        if self.creature_type == 'herbivore':
            self.radius = config.get('creatures.herbivore_radius')
        else:
            self.radius = config.get('creatures.carnivore_radius')
        
        self.food_eaten = 0
        self.distance_traveled = 0.0
        
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
        
        # Find nearest food
        nearest_food = self._find_nearest(
            environment.plants if self.creature_type == 'herbivore' 
            else environment.get_prey(self)
        )
        inputs.extend(nearest_food)
        
        # Find nearest threat
        nearest_threat = self._find_nearest(environment.get_predators(self))
        inputs.extend(nearest_threat)
        
        # Find nearest prey (for carnivores)
        if self.creature_type == 'carnivore':
            nearest_prey = self._find_nearest(environment.get_prey(self))
            inputs.extend(nearest_prey)
        else:
            inputs.extend([0, 0])
        
        input_neurons = config.get('neural_network.input_neurons')
        return inputs[:input_neurons]
    

    def _find_nearest(self, entities):
        """Find nearest entity from a list and return direction/distance"""
        if not entities:
            return [0.0, 0.0]  # Return normalized vector instead of tuple
        
        nearest = None
        min_dist = float('inf')
        
        for entity in entities:
            # Properly extract coordinates
            if hasattr(entity, 'x'):
                ex, ey = entity.x, entity.y
            else:
                ex, ey = entity[0], entity[1]
            
            dist = math.sqrt((self.x - ex)**2 + (self.y - ey)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = (ex, ey)
        
        if nearest is None:
            return [0.0, 0.0]
        
        # Return normalized direction vector
        dx = nearest[0] - self.x
        dy = nearest[1] - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            return [dx/dist, dy/dist]  # Normalized direction
        return [0.0, 0.0]
    

    def think_and_act(self, environment):
        """Process inputs through neural network and take action"""
        # Get sensory inputs
        inputs = self.get_inputs(environment)
        
        # Process through brain
        outputs = self.brain.forward(inputs)
        
        # Interpret outputs as actions
        # outputs should have 2 values: [turn_amount, move_speed]
        turn = outputs[0] * 0.2  # Scale turning
        speed = outputs[1] * 2.0  # Scale movement speed
        
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
        
        # Use energy for movement
        self.energy -= abs(speed) * 0.05 + abs(turn) * 0.03
    
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
        
        for plant in environment.plants[:]:
            dist = math.sqrt((plant[0] - self.x)**2 + (plant[1] - self.y)**2)
            if dist < self.radius + 5:
                environment.plants.remove(plant)
                self.energy = min(max_energy, self.energy + plant_energy)
                self.food_eaten += 1
                break
    
    def _attack_prey(self, environment: 'Environment') -> None:
        """Attack nearby herbivores."""
        max_energy = config.get('creatures.max_energy')
        
        for creature in environment.creatures:
            if creature.creature_type == 'herbivore' and creature.alive:
                dist = math.sqrt((creature.x - self.x)**2 + (creature.y - self.y)**2)
                if dist < self.radius + creature.radius:
                    creature.alive = False
                    self.energy = min(max_energy, self.energy + 50)
                    self.food_eaten += 1
                    break
    
    def update(self) -> None:
        """Update creature state."""
        self.age += 1
        self.energy -= 0.05  # Base metabolism
        
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
