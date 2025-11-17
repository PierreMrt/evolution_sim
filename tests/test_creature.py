"""Tests for creature functionality."""
import pytest
from evolution_sim.core.creature import Creature
from evolution_sim.core.genome import Genome


class TestCreature:
    """Test cases for Creature class."""
    
    def test_creature_initialization(self):
        """Test creature creation."""
        genome = Genome('herbivore')
        creature = Creature(100, 200, genome)
        
        assert creature.x == 100
        assert creature.y == 200
        assert creature.alive is True
        assert creature.energy > 0
        assert creature.age == 0
    
    def test_creature_id_uniqueness(self):
        """Test that each creature gets unique ID."""
        genome1 = Genome('herbivore')
        genome2 = Genome('herbivore')
        
        creature1 = Creature(0, 0, genome1)
        creature2 = Creature(0, 0, genome2)
        
        assert creature1.id != creature2.id
    
    def test_herbivore_properties(self):
        """Test herbivore-specific properties."""
        genome = Genome('herbivore')
        creature = Creature(0, 0, genome)
        
        assert creature.creature_type == 'herbivore'
        assert creature.radius == 8  # From config
    
    def test_carnivore_properties(self):
        """Test carnivore-specific properties."""
        genome = Genome('carnivore')
        creature = Creature(0, 0, genome)
        
        assert creature.creature_type == 'carnivore'
        assert creature.radius == 10  # From config
    
    def test_creature_update(self):
        """Test creature state update."""
        genome = Genome('herbivore')
        creature = Creature(0, 0, genome)
        
        initial_energy = creature.energy
        creature.update()
        
        assert creature.age == 1
        assert creature.energy < initial_energy  # Metabolism
    
    def test_creature_death_from_energy(self):
        """Test creature dies when energy depleted."""
        genome = Genome('herbivore')
        creature = Creature(0, 0, genome)
        
        creature.energy = 0
        creature.update()
        
        assert creature.alive is False
    
    def test_can_reproduce(self):
        """Test reproduction eligibility."""
        genome = Genome('herbivore')
        creature = Creature(0, 0, genome)
        
        # Young with low energy - cannot reproduce
        creature.energy = 50
        creature.age = 50
        assert creature.can_reproduce() is False
        
        # Old with high energy - can reproduce
        creature.energy = 80
        creature.age = 150
        assert creature.can_reproduce() is True
    
    def test_reproduce(self):
        """Test offspring creation."""
        genome = Genome('herbivore')
        parent = Creature(100, 100, genome)
        parent.energy = 80
        
        initial_energy = parent.energy
        offspring = parent.reproduce()
        
        # Check parent lost energy
        assert parent.energy < initial_energy
        
        # Check offspring properties
        assert offspring.alive is True
        assert offspring.creature_type == parent.creature_type
        assert offspring.id != parent.id
        
        # Offspring should be near parent
        distance = ((offspring.x - parent.x)**2 + (offspring.y - parent.y)**2)**0.5
        assert distance < 50
