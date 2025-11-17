"""Tests for evolution algorithms."""
import pytest
from evolution_sim.core.genome import Genome
from evolution_sim.evolution.mutation import MutationEngine
from evolution_sim.evolution.selection import SelectionEngine
from evolution_sim.evolution.species import Species, SpeciesManager


class TestMutationEngine:
    """Test cases for mutation operations."""
    
    def test_mutate_weights(self):
        """Test weight mutation."""
        genome = Genome('herbivore')
        original_weights = [c.weight for c in genome.network.connections]
        
        MutationEngine.mutate_weights(genome, strength=0.5)
        
        new_weights = [c.weight for c in genome.network.connections]
        # At least some weights should change
        assert original_weights != new_weights
    
    def test_mutate_add_node(self):
        """Test adding node mutation."""
        genome = Genome('herbivore')
        initial_neurons = len(genome.network.neurons)
        
        success = MutationEngine.mutate_add_node(genome)
        
        if success:
            assert len(genome.network.neurons) > initial_neurons
    
    def test_crossover(self):
        """Test genome crossover."""
        parent1 = Genome('herbivore')
        parent1.fitness = 100
        parent2 = Genome('herbivore')
        parent2.fitness = 50
        
        offspring = MutationEngine.crossover(parent1, parent2)
        
        assert offspring.creature_type == 'herbivore'
        assert len(offspring.network.neurons) > 0


class TestSelectionEngine:
    """Test cases for selection methods."""
    
    @pytest.fixture
    def genomes_with_fitness(self):
        """Create genomes with different fitness values."""
        genomes = []
        for i in range(10):
            genome = Genome('herbivore')
            genome.fitness = i * 10
            genomes.append(genome)
        return genomes
    
    def test_tournament_selection(self, genomes_with_fitness):
        """Test tournament selection."""
        selected = SelectionEngine.tournament_selection(genomes_with_fitness, tournament_size=3)
        
        assert selected in genomes_with_fitness
        assert selected.fitness >= 0
    
    def test_roulette_selection(self, genomes_with_fitness):
        """Test roulette wheel selection."""
        selected = SelectionEngine.roulette_wheel_selection(genomes_with_fitness)
        
        assert selected in genomes_with_fitness
    
    def test_elitism_selection(self, genomes_with_fitness):
        """Test elitism selection."""
        elite = SelectionEngine.elitism_selection(genomes_with_fitness, elite_count=3)
        
        assert len(elite) == 3
        # Should be top 3 by fitness
        assert elite[0].fitness >= elite[1].fitness
        assert elite[1].fitness >= elite[2].fitness


class TestSpecies:
    """Test cases for Species class."""
    
    def test_species_initialization(self):
        """Test species creation."""
        genome = Genome('herbivore')
        species = Species(0, genome)
        
        assert species.id == 0
        assert species.representative == genome
        assert len(species.members) == 0
    
    def test_add_member(self):
        """Test adding members to species."""
        genome1 = Genome('herbivore')
        species = Species(0, genome1)
        
        genome2 = Genome('herbivore')
        species.add_member(genome2)
        
        assert len(species.members) == 1
        assert genome2.species_id == 0


class TestSpeciesManager:
    """Test cases for SpeciesManager."""
    
    def test_manager_initialization(self):
        """Test species manager creation."""
        manager = SpeciesManager()
        
        assert len(manager.species) == 0
        assert manager.next_species_id == 0
    
    def test_speciate(self):
        """Test species assignment."""
        manager = SpeciesManager()
        
        # Create some genomes
        genomes = [Genome('herbivore') for _ in range(5)]
        
        manager.speciate(genomes)
        
        # Should create at least one species
        assert len(manager.species) > 0
        
        # All genomes should be assigned
        total_members = sum(len(s.members) for s in manager.species.values())
        assert total_members == len(genomes)
    
    def test_get_species_count(self):
        """Test species count."""
        manager = SpeciesManager()
        genomes = [Genome('herbivore') for _ in range(3)]
        
        manager.speciate(genomes)
        
        count = manager.get_species_count()
        assert count > 0
