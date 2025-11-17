"""Main environment and world simulation."""
import random
from typing import List, Tuple
from ..core.creature import Creature
from ..core.genome import Genome
from ..config import config


class Environment:
    """Simulation environment containing all creatures and resources."""
    
    def __init__(self):
        """Initialize the environment."""
        self.creatures: List[Creature] = []
        self.plants: List[Tuple[float, float]] = []
        self.generation = 0
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the environment with creatures and plants."""
        # Create initial herbivores
        initial_herbivores = config.get('creatures.initial_herbivores')
        for _ in range(initial_herbivores):
            genome = Genome('herbivore')
            x = random.uniform(50, config.get('world.width') - 50)
            y = random.uniform(50, config.get('world.height') - 50)
            self.creatures.append(Creature(x, y, genome))
        
        # Create initial carnivores
        initial_carnivores = config.get('creatures.initial_carnivores')
        for _ in range(initial_carnivores):
            genome = Genome('carnivore')
            x = random.uniform(50, config.get('world.width') - 50)
            y = random.uniform(50, config.get('world.height') - 50)
            self.creatures.append(Creature(x, y, genome))
        
        # Spawn plants
        initial_plants = config.get('world.initial_plants')
        for _ in range(initial_plants):
            self._spawn_plant()
    
    def _spawn_plant(self) -> None:
        """Spawn a new plant at a random location."""
        x = random.uniform(10, config.get('world.width') - 10)
        y = random.uniform(10, config.get('world.height') - 10)
        self.plants.append((x, y))
    
    def get_prey(self, creature: Creature) -> List[Creature]:
        """
        Get potential prey for a creature.
        
        Args:
            creature: The hunting creature
            
        Returns:
            List of prey creatures
        """
        if creature.creature_type == 'carnivore':
            return [c for c in self.creatures if c.creature_type == 'herbivore' and c.alive]
        return []
    
    def get_predators(self, creature: Creature) -> List[Creature]:
        """
        Get potential predators for a creature.
        
        Args:
            creature: The prey creature
            
        Returns:
            List of predator creatures
        """
        if creature.creature_type == 'herbivore':
            return [c for c in self.creatures if c.creature_type == 'carnivore' and c.alive]
        return []
    
    def update(self) -> None:
        """Update all entities in the environment."""
        # Update creatures
        for creature in self.creatures:
            if creature.alive:
                creature.think_and_act(self)
                creature.update()
        
        # Handle reproduction
        new_creatures = []
        for creature in self.creatures:
            if creature.alive and creature.can_reproduce():
                offspring = creature.reproduce()
                new_creatures.append(offspring)
        
        self.creatures.extend(new_creatures)
        
        # Remove dead creatures
        self.creatures = [c for c in self.creatures if c.alive]
        
        # Grow plants
        growth_rate = config.get('world.plant_growth_rate')
        initial_plants = config.get('world.initial_plants')
        if random.random() < growth_rate and len(self.plants) < initial_plants * 2:
            self._spawn_plant()
        
        # Prevent extinction
        self._prevent_extinction()
    
    def _prevent_extinction(self) -> None:
        """Spawn new creatures if population is too low."""
        herbivores = [c for c in self.creatures if c.creature_type == 'herbivore']
        carnivores = [c for c in self.creatures if c.creature_type == 'carnivore']
        
        world_width = config.get('world.width')
        world_height = config.get('world.height')
        
        if len(herbivores) < 2:
            for _ in range(3):
                genome = Genome('herbivore')
                x = random.uniform(50, world_width - 50)
                y = random.uniform(50, world_height - 50)
                self.creatures.append(Creature(x, y, genome))
        
        if len(carnivores) < 2:
            for _ in range(2):
                genome = Genome('carnivore')
                x = random.uniform(50, world_width - 50)
                y = random.uniform(50, world_height - 50)
                self.creatures.append(Creature(x, y, genome))
