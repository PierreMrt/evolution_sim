"""Mutation operators for evolutionary algorithms."""
import random
from typing import List
from ..core.genome import Genome
from ..config import config


class MutationEngine:
    """Handles all mutation operations for genomes."""
    
    @staticmethod
    def mutate_population(genomes: List[Genome]) -> None:
        """
        Apply mutations to a population of genomes.
        
        Args:
            genomes: List of genomes to mutate
        """
        mutation_rate = config.get('evolution.mutation_rate')
        
        for genome in genomes:
            if random.random() < mutation_rate:
                genome.mutate()
    
    @staticmethod
    def mutate_weights(genome: Genome, strength: float = None) -> None:
        """
        Mutate connection weights in a genome.
        
        Args:
            genome: Genome to mutate
            strength: Mutation strength (uses config default if None)
        """
        if strength is None:
            strength = config.get('evolution.weight_mutation_strength')
        
        for conn in genome.network.connections:
            if random.random() < 0.5:
                # Perturb weight
                conn.weight += random.gauss(0, strength)
            else:
                # Replace weight
                conn.weight = random.uniform(-1, 1)
            
            # Clamp weight
            conn.weight = max(-2, min(2, conn.weight))
    
    @staticmethod
    def mutate_add_node(genome: Genome) -> bool:
        """
        Add a new node to the genome by splitting a connection.
        
        Args:
            genome: Genome to mutate
            
        Returns:
            True if node was added successfully
        """
        max_neurons = config.get('neural_network.max_neurons')
        
        if len(genome.network.neurons) >= max_neurons:
            return False
        
        if not genome.network.connections:
            return False
        
        # Select random connection to split
        conn = random.choice(genome.network.connections)
        conn.enabled = False
        
        # Add new hidden neuron
        new_id = genome.network.add_neuron('hidden')
        
        # Add two new connections
        genome.network.add_connection(conn.from_neuron, new_id, 1.0)
        genome.network.add_connection(new_id, conn.to_neuron, conn.weight)
        
        return True
    
    @staticmethod
    def mutate_add_connection(genome: Genome) -> bool:
        """
        Add a new connection between two random neurons.
        
        Args:
            genome: Genome to mutate
            
        Returns:
            True if connection was added successfully
        """
        neurons = list(genome.network.neurons.keys())
        
        if len(neurons) < 2:
            return False
        
        # Try to find valid connection
        max_attempts = 10
        for _ in range(max_attempts):
            from_id = random.choice(neurons)
            to_id = random.choice(neurons)
            
            if from_id == to_id:
                continue
            
            # Check if connection already exists
            exists = any(
                c.from_neuron == from_id and c.to_neuron == to_id 
                for c in genome.network.connections
            )
            
            if not exists:
                weight = random.uniform(-1, 1)
                genome.network.add_connection(from_id, to_id, weight)
                return True
        
        return False
    
    @staticmethod
    def mutate_remove_node(genome: Genome) -> bool:
        """
        Remove a random hidden node from the genome.
        
        Args:
            genome: Genome to mutate
            
        Returns:
            True if node was removed successfully
        """
        hidden_neurons = [
            n.id for n in genome.network.neurons.values() 
            if n.type == 'hidden'
        ]
        
        if not hidden_neurons:
            return False
        
        remove_id = random.choice(hidden_neurons)
        del genome.network.neurons[remove_id]
        
        # Remove all connections involving this neuron
        genome.network.connections = [
            c for c in genome.network.connections 
            if c.from_neuron != remove_id and c.to_neuron != remove_id
        ]
        
        return True
    
    @staticmethod
    def crossover(parent1: Genome, parent2: Genome) -> Genome:
        """
        Create offspring by combining two parent genomes.
        
        Args:
            parent1: First parent genome
            parent2: Second parent genome
            
        Returns:
            New offspring genome
        """
        # Select the more fit parent
        if parent1.fitness >= parent2.fitness:
            primary, secondary = parent1, parent2
        else:
            primary, secondary = parent2, parent1
        
        # Create offspring as copy of primary parent
        offspring = primary.copy()
        
        # Inherit some connections from secondary parent
        for conn in secondary.network.connections:
            # Check if connection exists in primary
            matching = None
            for p_conn in offspring.network.connections:
                if (p_conn.from_neuron == conn.from_neuron and 
                    p_conn.to_neuron == conn.to_neuron):
                    matching = p_conn
                    break
            
            # 50% chance to inherit weight from secondary parent
            if matching and random.random() < 0.5:
                matching.weight = conn.weight
                matching.enabled = conn.enabled
        
        return offspring
