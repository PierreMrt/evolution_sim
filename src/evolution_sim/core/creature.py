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
        
        # CARNIVORES START WITH SLIGHTLY LESS ENERGY
        if self.creature_type == 'carnivore':
            self.energy = max_energy * 0.60  # CHANGED: was 0.7
        else:
            self.energy = max_energy * 0.5  # 50% energy
        
        self.age = 0
        self.alive = True
        
        # Random initial direction
        self.direction = random.uniform(0, 2 * math.pi)
        
        # CARNIVORES ARE LARGER AND SLIGHTLY FASTER
        if self.creature_type == 'herbivore':
            self.radius = config.get('creatures.herbivore_radius')
            self.speed_multiplier = 1.0  # Normal speed
        else:
            self.radius = config.get('creatures.carnivore_radius')
            self.speed_multiplier = 1.07  # CHANGED: was 1.1
        
        self.food_eaten = 0
        self.distance_traveled = 0.0
        self.eat_cooldown = 0
        
        self.time_since_reproduction = 0
        
        self.food_history = []
        self.food_history_window = 50
        self.last_food_count = 0
        
        # Migration control
        self.migration_cooldown = 0
        self.is_migrating = False
        self.migration_target = None
        
        # Reproduction urge tracking
        self.reproduction_desire = 0.0  # Store last output value
        
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
        
        # New neuron inputs
        inputs.append(self._sense_local_density(environment))
        inputs.append(self._get_food_scarcity_signal())
        inputs.append(self._get_reproduction_readiness())
        
        input_neurons = config.get('neural_network.input_neurons')
        return inputs[:input_neurons]
    

    def _sense_local_density(self, environment: 'Environment') -> float:
        """Return normalized count of same-type creatures nearby (crowding/isolation)."""
        sensing_radius = self.radius * 15
        if hasattr(environment, 'spatial_grid'):
            nearby = environment.spatial_grid.query_neighborhood(
                self.x, self.y, self.creature_type
            )
        else:
            nearby = [c for c in environment.creatures
                      if c.creature_type == self.creature_type
                      and c.id != self.id
                      and getattr(c, 'alive', True)]
        count = 0
        for creature in nearby:
            if hasattr(creature, 'x'):
                dist = math.hypot(creature.x - self.x, creature.y - self.y)
                if dist < sensing_radius:
                    count += 1
        return min(1.0, count / 20.0)
    
    def _update_food_history(self) -> None:
        """Update rolling average of food eaten per step."""
        food_gained_this_step = self.food_eaten - self.last_food_count
        self.food_history.append(food_gained_this_step)
        if len(self.food_history) > self.food_history_window:
            self.food_history.pop(0)
        self.last_food_count = self.food_eaten

    def _get_food_scarcity_signal(self) -> float:
        """Return normalized food scarcity signal based on recent consumption."""
        if len(self.food_history) < 10:
            return 0.5
        avg_food_rate = sum(self.food_history) / len(self.food_history)
        target_rate = 0.05 if self.creature_type == 'herbivore' else 0.02
        scarcity = 1.0 - min(1.0, avg_food_rate / target_rate)
        return scarcity
    
    def _get_reproduction_readiness(self) -> float:
        """Return normalized reproduction readiness based on time since last reproduction."""
        if self.creature_type == 'herbivore':
            typical_interval = 300
        else:
            typical_interval = 400
        return min(1.0, self.time_since_reproduction / typical_interval)
    
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
        
        # Output 0: Turn angle
        turn = outputs[0] * 0.2
        
        # Output 1: Movement speed
        base_speed = outputs[1] * 2.0
        
        # Output 2: Reproduction urge (continuous value 0-1)
        self.reproduction_desire = max(0.0, min(1.0, outputs[2]))
        
        # Output 3: Migration trigger (continuous value 0-1)
        migration_urge = max(0.0, min(1.0, outputs[3])) if len(outputs) > 3 else 0.0
        
        # Handle migration
        self._handle_migration(migration_urge, environment)
        
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
        
        # CARNIVORES PAY SLIGHTLY MORE FOR MOVEMENT (more balanced)
        if self.creature_type == 'carnivore':
            self.energy -= abs(speed) * 0.023 + abs(turn) * 0.017
        else:
            self.energy -= abs(speed) * 0.03 + abs(turn) * 0.02
        
        # Try to eat
        self.try_eat(environment)

    
    def _handle_migration(self, migration_urge: float, environment: 'Environment') -> None:
        """
        Handle long-distance migration based on neural output.
        
        Args:
            migration_urge: Output value from neural network (0-1)
            environment: The simulation environment
        """
        # Decay cooldown
        if self.migration_cooldown > 0:
            self.migration_cooldown -= 1
            return
        
        # Migration threshold (can be made configurable)
        migration_threshold = config.get('creatures.migration_threshold', 0.7)
        
        # Trigger migration if urge exceeds threshold
        if migration_urge > migration_threshold and not self.is_migrating:
            self._initiate_migration(environment)
        
        # Execute migration if active
        if self.is_migrating:
            self._execute_migration()

    def _initiate_migration(self, environment: 'Environment') -> None:
        """Start a migration event."""
        world_width = config.get('world.width')
        world_height = config.get('world.height')
        
        # Choose random distant target
        migration_distance = random.uniform(200, 400)  # Configurable distance
        angle = random.uniform(0, 2 * math.pi)
        
        target_x = self.x + migration_distance * math.cos(angle)
        target_y = self.y + migration_distance * math.sin(angle)
        
        # Wrap coordinates
        target_x = target_x % world_width
        target_y = target_y % world_height
        
        self.migration_target = (target_x, target_y)
        self.is_migrating = True
        
        # Energy cost for initiating migration
        migration_cost = config.get('creatures.migration_energy_cost', 15)
        self.energy -= migration_cost

    def _execute_migration(self) -> None:
        """Move toward migration target at increased speed."""
        if self.migration_target is None:
            self.is_migrating = False
            return
        
        target_x, target_y = self.migration_target
        
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Handle world wrapping (shortest path)
        world_width = config.get('world.width')
        world_height = config.get('world.height')
        
        if abs(dx) > world_width / 2:
            dx = dx - math.copysign(world_width, dx)
        if abs(dy) > world_height / 2:
            dy = dy - math.copysign(world_height, dy)
        
        distance = math.hypot(dx, dy)
        
        # Arrived at target or close enough
        if distance < 20:
            self.is_migrating = False
            self.migration_target = None
            self.migration_cooldown = config.get('creatures.migration_cooldown', 300)  # Prevent immediate re-migration
            return
        
        # Move toward target with boosted speed
        if distance > 0:
            self.direction = math.atan2(dy, dx)
            migration_speed = 3.0 * self.speed_multiplier  # Faster during migration
            
            move_x = (dx / distance) * migration_speed
            move_y = (dy / distance) * migration_speed
            
            self.x += move_x
            self.y += move_y
            
            # Wrap around edges
            self.x = self.x % world_width
            self.y = self.y % world_height
    
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
                self.energy = min(max_energy, self.energy + config.get('world.herbivores_energy_eaten'))
                self.food_eaten += 1
                break
    
    def update(self) -> None:
        """Update creature state."""
        self.time_since_reproduction += 1
        self._update_food_history()
        
        # Decay migration cooldown
        if self.migration_cooldown > 0:
            self.migration_cooldown -= 1
        
        self.age += 1
        self.energy -= 0.03  # Base metabolism
        
        if self.energy <= 0:
            self.alive = False
        
        # Calculate fitness
        self.genome.fitness = (
            0.3 * (self.food_eaten * 8 / max(1, self.distance_traveled * 0.015)) +
            0.7 * ((self.age ** 0.5) * 4 + self.children_count * 18) +
            - (len(self.genome.network.neurons) * 0.25)
        )
    
    def can_reproduce(self) -> bool:
        """
        Check if creature can reproduce based on thresholds AND neural urge.
        
        Returns:
            True if creature meets all reproduction conditions
        """
        # Basic energy and age requirements
        if self.creature_type == 'herbivore':
            energy_threshold = config.get('creatures.herbivores_reproduction_energy_threshold')
            min_reproductive_age = config.get('creatures.herbivores_min_reproductive_age', 250)
        else:
            energy_threshold = config.get('creatures.carnivores_reproduction_energy_threshold')
            min_reproductive_age = config.get('creatures.carnivores_min_reproductive_age', 300)
        
        basic_requirements = self.energy > energy_threshold and self.age > min_reproductive_age
        
        if not basic_requirements:
            return False
        
        # Neural control: check reproduction desire output
        reproduction_threshold = config.get('creatures.reproduction_desire_threshold', 0.6)
        
        return self.reproduction_desire > reproduction_threshold
    
    def reproduce(self) -> 'Creature':
        """
        Create offspring with mutations.
        
        Returns:
            New Creature instance (offspring)
        """

        if self.creature_type == 'herbivore':
            repro_cost = config.get('creatures.herbivores_reproduction_cost')
            max_age_for_full_reproduction = config.get('creatures.herbivores_max_age_for_reproduction', 2000)
            senescence_period = config.get('creatures.herbivores_senescence_period', 1000)
        else:            
            repro_cost = config.get('creatures.carnivores_reproduction_cost')
            max_age_for_full_reproduction = config.get('creatures.carnivores_max_age_for_reproduction', 1800)
            senescence_period = config.get('creatures.carnivores_senescence_period', 800)

        if self.age > max_age_for_full_reproduction:
            repro_cost = int(repro_cost * (1 + (self.age - max_age_for_full_reproduction) / senescence_period))

        self.energy -= repro_cost
        self.time_since_reproduction = 0
        
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
