"""Track evolutionary progress and statistics."""

from typing import List, Dict, Optional
from collections import deque
import time

class CreatureRecord:
    """Record of a creature's lifetime."""
    
    def __init__(self, creature_id: int, creature_type: str, generation: int, 
                 parent_id: Optional[int], birth_time: int):
        self.id = creature_id
        self.type = creature_type
        self.generation = generation
        self.parent_id = parent_id
        self.birth_time = birth_time
        self.death_time = None
        self.lifespan = 0
        self.food_eaten = 0
        self.fitness = 0
        self.children_count = 0
        self.neurons = 0
        self.connections = 0

class EvolutionTracker:
    """Tracks evolutionary progress and historical data."""
    
    def __init__(self, history_length: int = 1000):
        """
        Initialize the evolution tracker.
        
        Args:
            history_length: Number of frames to keep in history
        """
        self.history_length = history_length
        self.current_frame = 0
        
        # Historical data
        self.population_history = deque(maxlen=history_length)
        self.herbivore_history = deque(maxlen=history_length)
        self.carnivore_history = deque(maxlen=history_length)
        self.avg_fitness_history = deque(maxlen=history_length)
        self.avg_age_history = deque(maxlen=history_length)
        
        # All-time records
        self.all_creatures: Dict[int, CreatureRecord] = {}
        self.best_herbivore: Optional[CreatureRecord] = None
        self.best_carnivore: Optional[CreatureRecord] = None
        self.longest_lived: Optional[CreatureRecord] = None
        self.most_children: Optional[CreatureRecord] = None
        
        # Current generation stats
        self.max_generation = 0
        self.total_births = 0
        self.total_deaths = 0
        
    def register_birth(self, creature) -> None:
        """Register a new creature birth."""
        record = CreatureRecord(
            creature.id,
            creature.creature_type,
            creature.generation,
            creature.parent_id,
            self.current_frame
        )
        record.neurons = len(creature.genome.network.neurons)
        record.connections = len(creature.genome.network.connections)
        
        self.all_creatures[creature.id] = record
        self.total_births += 1
        self.max_generation = max(self.max_generation, creature.generation)
        creature.birth_time = self.current_frame
    
    def register_death(self, creature) -> None:
        """Register a creature death and update records."""
        if creature.id not in self.all_creatures:
            return
        
        record = self.all_creatures[creature.id]
        record.death_time = self.current_frame
        record.lifespan = creature.age
        record.food_eaten = creature.food_eaten
        record.fitness = creature.genome.fitness
        record.children_count = creature.children_count
        
        self.total_deaths += 1
        
        # Update best records
        if record.type == 'herbivore':
            if self.best_herbivore is None or record.fitness > self.best_herbivore.fitness:
                self.best_herbivore = record
        else:
            if self.best_carnivore is None or record.fitness > self.best_carnivore.fitness:
                self.best_carnivore = record
        
        if self.longest_lived is None or record.lifespan > self.longest_lived.lifespan:
            self.longest_lived = record
        
        if self.most_children is None or record.children_count > self.most_children.children_count:
            self.most_children = record
    
    def update(self, environment) -> None:
        """Update historical statistics."""
        herbivores = [c for c in environment.creatures if c.creature_type == 'herbivore']
        carnivores = [c for c in environment.creatures if c.creature_type == 'carnivore']
        
        self.population_history.append(len(environment.creatures))
        self.herbivore_history.append(len(herbivores))
        self.carnivore_history.append(len(carnivores))
        
        if environment.creatures:
            avg_fitness = sum(c.genome.fitness for c in environment.creatures) / len(environment.creatures)
            avg_age = sum(c.age for c in environment.creatures) / len(environment.creatures)
            self.avg_fitness_history.append(avg_fitness)
            self.avg_age_history.append(avg_age)
        else:
            self.avg_fitness_history.append(0)
            self.avg_age_history.append(0)
        
        self.current_frame += 1
    
    def get_lineage(self, creature_id: int) -> List[CreatureRecord]:
        """Get the lineage (ancestry) of a creature."""
        lineage = []
        current_id = creature_id
        
        while current_id is not None and current_id in self.all_creatures:
            record = self.all_creatures[current_id]
            lineage.append(record)
            current_id = record.parent_id
        
        return lineage
    
    def get_top_performers(self, n: int = 5) -> Dict[str, List[CreatureRecord]]:
        """Get top N performers in various categories."""
        all_records = list(self.all_creatures.values())
        
        # Filter only dead creatures for fair comparison
        dead_records = [r for r in all_records if r.death_time is not None]
        
        return {
            'fitness': sorted(dead_records, key=lambda r: r.fitness, reverse=True)[:n],
            'lifespan': sorted(dead_records, key=lambda r: r.lifespan, reverse=True)[:n],
            'children': sorted(dead_records, key=lambda r: r.children_count, reverse=True)[:n],
            'food': sorted(dead_records, key=lambda r: r.food_eaten, reverse=True)[:n],
        }
