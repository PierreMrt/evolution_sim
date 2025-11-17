"""Neural network implementation for creature brains."""
import numpy as np
import random
from typing import List, Dict

class Neuron:
    """Individual neuron in the neural network."""
    
    def __init__(self, neuron_id: int, neuron_type: str):
        """
        Initialize a neuron.
        
        Args:
            neuron_id: Unique identifier for the neuron
            neuron_type: Type of neuron ('input', 'hidden', 'output')
        """
        self.id = neuron_id
        self.type = neuron_type
        self.value = 0.0
        self.bias = random.uniform(-2, 2)
    
    def activate(self, x: float) -> float:
        """
        Apply sigmoid activation function.
        
        Args:
            x: Input value
            
        Returns:
            Activated output value
        """
        return 1 / (1 + np.exp(-max(-20, min(20, x))))


class Connection:
    """Connection between two neurons."""
    
    def __init__(self, from_neuron: int, to_neuron: int, weight: float, enabled: bool = True):
        """
        Initialize a connection.
        
        Args:
            from_neuron: Source neuron ID
            to_neuron: Destination neuron ID
            weight: Connection weight
            enabled: Whether connection is active
        """
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight = weight
        self.enabled = enabled
        self.innovation = (from_neuron, to_neuron)


class NeuralNetwork:
    """Feed-forward neural network with dynamic topology."""
    
    def __init__(self):
        """Initialize an empty neural network."""
        self.neurons: Dict[int, Neuron] = {}
        self.connections: List[Connection] = []
        self.next_neuron_id = 0
        
    def add_neuron(self, neuron_type: str) -> int:
        """
        Add a new neuron to the network.
        
        Args:
            neuron_type: Type of neuron to add
            
        Returns:
            ID of the newly created neuron
        """
        neuron_id = self.next_neuron_id
        self.neurons[neuron_id] = Neuron(neuron_id, neuron_type)
        self.next_neuron_id += 1
        return neuron_id
    
    def add_connection(self, from_id: int, to_id: int, weight: float) -> None:
        """
        Add a connection between two neurons.
        
        Args:
            from_id: Source neuron ID
            to_id: Destination neuron ID
            weight: Connection weight
        """
        # Avoid duplicate connections
        for conn in self.connections:
            if conn.from_neuron == from_id and conn.to_neuron == to_id:
                return
        self.connections.append(Connection(from_id, to_id, weight))
    
    def forward(self, inputs: List[float]) -> List[float]:
        """
        Perform forward pass through the network.
        
        Args:
            inputs: Input values for the network
            
        Returns:
            Output values from the network
        """
        # Reset neuron values
        for neuron in self.neurons.values():
            neuron.value = 0.0
        
        # Set input values
        input_neurons = [n for n in self.neurons.values() if n.type == 'input']
        for i, neuron in enumerate(input_neurons):
            if i < len(inputs):
                neuron.value = inputs[i]
        
        # Process hidden neurons
        hidden_neurons = [n for n in self.neurons.values() if n.type == 'hidden']
        for hidden in hidden_neurons:
            incoming_sum = hidden.bias
            for conn in self.connections:
                if conn.to_neuron == hidden.id and conn.enabled:
                    if conn.from_neuron in self.neurons:
                        incoming_sum += self.neurons[conn.from_neuron].value * conn.weight
            hidden.value = hidden.activate(incoming_sum)
        
        # Process output neurons
        output_neurons = [n for n in self.neurons.values() if n.type == 'output']
        outputs = []
        for output in output_neurons:
            incoming_sum = output.bias
            for conn in self.connections:
                if conn.to_neuron == output.id and conn.enabled:
                    if conn.from_neuron in self.neurons:
                        incoming_sum += self.neurons[conn.from_neuron].value * conn.weight
            output.value = output.activate(incoming_sum)
            outputs.append(output.value)
        
        return outputs
    
    def copy(self) -> 'NeuralNetwork':
        """
        Create a deep copy of the network.
        
        Returns:
            New NeuralNetwork instance with copied structure
        """
        new_net = NeuralNetwork()
        new_net.next_neuron_id = self.next_neuron_id
        
        for nid, neuron in self.neurons.items():
            new_neuron = Neuron(neuron.id, neuron.type)
            new_neuron.bias = neuron.bias
            new_net.neurons[nid] = new_neuron
        
        for conn in self.connections:
            new_net.connections.append(
                Connection(conn.from_neuron, conn.to_neuron, conn.weight, conn.enabled)
            )
        
        return new_net
