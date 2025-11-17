"""Tests for genome functionality."""
import pytest
from evolution_sim.core.genome import Genome


class TestGenome:
    """Test cases for Genome class."""
    
    def test_genome_initialization(self):
        """Test genome creation."""
        genome = Genome('herbivore')
        assert genome.creature_type == 'herbivore'
        assert genome.fitness == 0
        assert genome.network is not None
    
    def test_initial_network_structure(self):
        """Test that genome initializes with proper network."""
        genome = Genome('carnivore')
        
        # Should have input and output neurons
        assert len(genome.network.neurons) > 0
        assert len(genome.network.connections) > 0
        
        # Check neuron types
        neuron_types = [n.type for n in genome.network.neurons.values()]
        assert 'input' in neuron_types
        assert 'output' in neuron_types
    
    def test_genome_mutate(self):
        """Test mutation doesn't break genome."""
        genome = Genome('herbivore')
        initial_neurons = len(genome.network.neurons)
        
        # Mutate multiple times
        for _ in range(10):
            genome.mutate()
        
        # Network should still be valid
        assert len(genome.network.neurons) > 0
        assert len(genome.network.connections) >= 0
    
    def test_genome_copy(self):
        """Test genome copying."""
        original = Genome('carnivore')
        original.fitness = 100
        
        copy = original.copy()
        
        assert copy.creature_type == original.creature_type
        assert copy.fitness == 0  # Fitness is reset
        assert len(copy.network.neurons) == len(original.network.neurons)
        
        # Test deep copy
        copy.network.neurons[0].bias = 999
        assert original.network.neurons[0].bias != 999
    
    def test_different_creature_types(self):
        """Test creating different creature types."""
        herb = Genome('herbivore')
        carn = Genome('carnivore')
        
        assert herb.creature_type == 'herbivore'
        assert carn.creature_type == 'carnivore'
