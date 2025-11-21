"""Main environment and world simulation."""
import random
from typing import List, Tuple
from ..core.creature import Creature
from ..core.genome import Genome
from ..config import config
from ..spatial.spatial_hash_grid import SpatialHashGrid


class Environment:
    """Simulation environment containing all creatures and resources."""
    
    def __init__(self):
        """Initialize the environment."""
        self.creatures: List[Creature] = []
        self.plants: List[Tuple[float, float]] = []
        self.generation = 0
        # Spatial grid for neighbor queries (built each frame)
        cell_size = max(1, config.get('neural_network.vision_range') or 50)
        self.spatial_grid = SpatialHashGrid(
            config.get('world.width'), config.get('world.height'), cell_size
        )
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
        """Spawn a plant, possibly near other plants (clustering)."""
        world_width = config.get('world.width')
        world_height = config.get('world.height')
        
        # 60% chance to spawn near existing plant (cluster)
        if self.plants and random.random() < 0.6:
            # Pick a random existing plant
            base_plant = random.choice(self.plants)
            # Spawn nearby (within 100 pixels)
            x = base_plant[0] + random.uniform(-100, 100)
            y = base_plant[1] + random.uniform(-100, 100)
            
            # Clamp to world bounds
            x = max(10, min(world_width - 10, x))
            y = max(10, min(world_height - 10, y))
        else:
            # Random location
            x = random.uniform(10, world_width - 10)
            y = random.uniform(10, world_height - 10)
        
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
        # Rebuild spatial grid each frame for fast neighbor queries
        try:
            self.spatial_grid.clear()
            # Insert plants
            for plant in self.plants:
                # plant is a (x,y) tuple
                self.spatial_grid.insert(plant, plant[0], plant[1], 'plant')
            # Insert creatures
            for creature in self.creatures:
                if creature.alive:
                    self.spatial_grid.insert(creature, creature.x, creature.y, creature.creature_type)
        except Exception:
            # If spatial grid is not available for any reason, continue using full scans
            pass

        # Update creatures
        for creature in self.creatures:
            if creature.alive:
                creature.think_and_act(self)
                creature.try_eat(self)  # Make sure this is here
                creature.update()
        
        # Handle reproduction
        new_creatures = []
        for creature in self.creatures:
            if creature.alive and creature.can_reproduce():
                offspring = creature.reproduce()
                new_creatures.append(offspring)
        
        self.creatures.extend(new_creatures)
        
        # Track deaths before removing
        dead_creatures = [c for c in self.creatures if not c.alive]
        
        # Remove dead creatures
        self.creatures = [c for c in self.creatures if c.alive]
        
        # Return dead creatures so Simulation can register them
        self.dead_this_frame = dead_creatures
        
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
