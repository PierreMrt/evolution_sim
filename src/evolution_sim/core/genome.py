"""Genetic encoding for creatures."""
import random
from .neural_network import NeuralNetwork
from ..config import config


class Genome:
    """Genetic representation of a creature."""
    
    def __init__(self, creature_type: str):
        """
        Initialize a genome.
        
        Args:
            creature_type: Type of creature ('herbivore' or 'carnivore')
        """
        self.creature_type = creature_type
        self.network = NeuralNetwork()
        self.fitness = 0
        self.species_id = None
        self._initialize_network()
    
    def _initialize_network(self) -> None:
        """Create initial fully-connected network structure."""
        input_neurons = config.get('neural_network.input_neurons')
        output_neurons = config.get('neural_network.output_neurons')
        
        # Add input neurons
        for _ in range(input_neurons):
            self.network.add_neuron('input')
        
        # Add output neurons
        for _ in range(output_neurons):
            self.network.add_neuron('output')
            
        # Connect inputs to outputs with SPECIES-SPECIFIC biases
        for i in range(input_neurons):
            for o in range(input_neurons, input_neurons + output_neurons):
                output_index = o - input_neurons
                
                # Determine weight based on input and output type
                if self.creature_type == 'carnivore':
                    # AGGRESSIVE CARNIVORE BIAS
                    if i in [6, 7]:  # Prey direction inputs (inputs 6-7)
                        if output_index == 0:  # Turn toward prey
                            weight = random.uniform(2.0, 4.0)  # STRONG positive
                        elif output_index == 1:  # Speed toward prey
                            weight = random.uniform(2.0, 4.0)  # STRONG positive
                        else:  # Sprint when hunting
                            weight = random.uniform(1.0, 2.5)  # Strong positive
                    else:
                        # Other inputs have normal weights
                        if output_index == 0:  # Turn
                            weight = random.uniform(-0.5, 0.5)
                        elif output_index == 1:  # Speed - forward bias
                            weight = random.uniform(0.8, 2.0)
                        else:
                            weight = random.uniform(-1, 1)
                else:
                    # HERBIVORE - forward movement bias
                    if output_index == 0:  # Turn - small weights
                        weight = random.uniform(-0.5, 0.5)
                    elif output_index == 1:  # Speed - forward bias
                        weight = random.uniform(0.8, 2.0)
                    else:
                        weight = random.uniform(-1, 1)
                
                self.network.add_connection(i, o, weight)
        
        # Compile arrays after building initial network
        self.network._compile_to_arrays()
    
    def mutate(self) -> None:
        """Apply various mutations to the genome."""
        self._mutate_weights()
        self._mutate_biases()
        self._mutate_add_neuron()
        self._mutate_remove_neuron()
        self._mutate_add_connection()
        # Compile arrays after any mutation
        self.network._compile_to_arrays()
    
    def _mutate_weights(self) -> None:
        """Mutate connection weights."""
        weight_mut_rate = config.get('evolution.weight_mutation_rate')
        weight_mut_strength = config.get('evolution.weight_mutation_strength')
        
        if random.random() < weight_mut_rate:
            for conn in self.network.connections:
                if random.random() < 0.5:
                    conn['weight'] += random.gauss(0, weight_mut_strength)
                else:
                    conn['weight'] = random.uniform(-1, 1)
                conn['weight'] = max(-2, min(2, conn['weight']))
    
    def _mutate_biases(self) -> None:
        """Mutate neuron biases."""
        weight_mut_rate = config.get('evolution.weight_mutation_rate')
        weight_mut_strength = config.get('evolution.weight_mutation_strength')
        
        for neuron in self.network.neurons.values():
            if random.random() < weight_mut_rate * 0.5:
                neuron['bias'] += random.gauss(0, weight_mut_strength)
                neuron['bias'] = max(-2, min(2, neuron['bias']))
    
    def _mutate_add_neuron(self) -> None:
        """Add a new neuron by splitting an existing connection."""
        add_neuron_rate = config.get('evolution.add_neuron_rate')
        max_neurons = config.get('neural_network.max_neurons')
        
        if random.random() < add_neuron_rate and len(self.network.neurons) < max_neurons:
            if self.network.connections:
                conn = random.choice(self.network.connections)
                conn['enabled'] = False
                
                new_id = self.network.add_neuron('hidden')
                self.network.add_connection(conn['from'], new_id, 1.0)
                self.network.add_connection(new_id, conn['to'], conn['weight'])
    
    def _mutate_remove_neuron(self) -> None:
        """Remove a random hidden neuron."""
        remove_neuron_rate = config.get('evolution.remove_neuron_rate')
        
        if random.random() < remove_neuron_rate:
            hidden_neurons = [n['id'] for n in self.network.neurons.values() if n['type'] == 'hidden']
            if hidden_neurons:
                remove_id = random.choice(hidden_neurons)
                del self.network.neurons[remove_id]
                self.network.connections = [
                    c for c in self.network.connections 
                    if c['from'] != remove_id and c['to'] != remove_id
                ]
    
    def _mutate_add_connection(self) -> None:
        """Add a new random connection."""
        add_conn_rate = config.get('evolution.add_connection_rate')
        
        if random.random() < add_conn_rate:
            neurons = list(self.network.neurons.keys())
            if len(neurons) >= 2:
                from_id = random.choice(neurons)
                to_id = random.choice(neurons)
                if from_id != to_id:
                    self.network.add_connection(from_id, to_id, random.uniform(-1, 1))
    
    def copy(self) -> 'Genome':
        """
        Create a copy of the genome.
        
        Returns:
            New Genome instance with copied structure
        """
        new_genome = Genome(self.creature_type)
        new_genome.network = self.network.copy()
        new_genome.species_id = self.species_id
        # ensure arrays compiled
        new_genome.network._compile_to_arrays()
        return new_genome
