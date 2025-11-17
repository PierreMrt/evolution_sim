"""Tests for neural network functionality."""
import pytest
from evolution_sim.core.neural_network import Neuron, Connection, NeuralNetwork


class TestNeuron:
    """Test cases for Neuron class."""
    
    def test_neuron_initialization(self):
        """Test that neurons initialize correctly."""
        neuron = Neuron(0, 'input')
        assert neuron.id == 0
        assert neuron.type == 'input'
        assert neuron.value == 0.0
        assert -1 <= neuron.bias <= 1
    
    def test_neuron_activation(self):
        """Test sigmoid activation function."""
        neuron = Neuron(0, 'hidden')
        
        # Test activation at 0
        result = neuron.activate(0)
        assert 0.4 < result < 0.6  # Should be close to 0.5
        
        # Test activation with positive input
        result_positive = neuron.activate(5)
        assert result_positive > 0.9
        
        # Test activation with negative input
        result_negative = neuron.activate(-5)
        assert result_negative < 0.1
    
    def test_activation_bounds(self):
        """Test that activation handles extreme values."""
        neuron = Neuron(0, 'hidden')
        
        # Should not overflow
        result_high = neuron.activate(100)
        assert 0 <= result_high <= 1
        
        result_low = neuron.activate(-100)
        assert 0 <= result_low <= 1


class TestConnection:
    """Test cases for Connection class."""
    
    def test_connection_initialization(self):
        """Test connection creation."""
        conn = Connection(0, 1, 0.5)
        assert conn.from_neuron == 0
        assert conn.to_neuron == 1
        assert conn.weight == 0.5
        assert conn.enabled is True
    
    def test_connection_innovation(self):
        """Test innovation number assignment."""
        conn1 = Connection(0, 1, 0.5)
        conn2 = Connection(0, 1, 0.7)
        assert conn1.innovation == conn2.innovation  # Same connection
        
        conn3 = Connection(1, 2, 0.5)
        assert conn1.innovation != conn3.innovation  # Different connection


class TestNeuralNetwork:
    """Test cases for NeuralNetwork class."""
    
    def test_network_initialization(self):
        """Test empty network creation."""
        network = NeuralNetwork()
        assert len(network.neurons) == 0
        assert len(network.connections) == 0
        assert network.next_neuron_id == 0
    
    def test_add_neuron(self):
        """Test adding neurons to network."""
        network = NeuralNetwork()
        
        id1 = network.add_neuron('input')
        assert id1 == 0
        assert len(network.neurons) == 1
        
        id2 = network.add_neuron('output')
        assert id2 == 1
        assert len(network.neurons) == 2
    
    def test_add_connection(self):
        """Test adding connections between neurons."""
        network = NeuralNetwork()
        network.add_neuron('input')
        network.add_neuron('output')
        
        network.add_connection(0, 1, 0.5)
        assert len(network.connections) == 1
        assert network.connections[0].weight == 0.5
    
    def test_prevent_duplicate_connections(self):
        """Test that duplicate connections are prevented."""
        network = NeuralNetwork()
        network.add_neuron('input')
        network.add_neuron('output')
        
        network.add_connection(0, 1, 0.5)
        network.add_connection(0, 1, 0.7)  # Duplicate
        
        assert len(network.connections) == 1  # Should still be 1
    
    def test_forward_pass_simple(self):
        """Test forward pass with simple network."""
        network = NeuralNetwork()
        
        # Create 2-1 network
        in1 = network.add_neuron('input')
        in2 = network.add_neuron('input')
        out1 = network.add_neuron('output')
        
        network.add_connection(in1, out1, 1.0)
        network.add_connection(in2, out1, 1.0)
        
        # Test forward pass
        outputs = network.forward([0.5, 0.5])
        assert len(outputs) == 1
        assert 0 <= outputs[0] <= 1  # Valid activation
    
    def test_forward_pass_with_hidden(self):
        """Test forward pass with hidden layer."""
        network = NeuralNetwork()
        
        in1 = network.add_neuron('input')
        hidden1 = network.add_neuron('hidden')
        out1 = network.add_neuron('output')
        
        network.add_connection(in1, hidden1, 1.0)
        network.add_connection(hidden1, out1, 1.0)
        
        outputs = network.forward([1.0])
        assert len(outputs) == 1
        assert 0 <= outputs[0] <= 1
    
    def test_network_copy(self):
        """Test deep copying of network."""
        network = NeuralNetwork()
        network.add_neuron('input')
        network.add_neuron('output')
        network.add_connection(0, 1, 0.5)
        
        copy = network.copy()
        
        # Test structure is copied
        assert len(copy.neurons) == len(network.neurons)
        assert len(copy.connections) == len(network.connections)
        
        # Test it's a deep copy
        copy.neurons[0].bias = 999
        assert network.neurons[0].bias != 999
