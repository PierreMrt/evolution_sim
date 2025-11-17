"""Species management for maintaining diversity."""
import random
from typing import List, Dict
from ..core.genome import Genome
from ..config import config


class Species:
    """Represents a species of similar genomes."""
    
    def __init__(self, species_id: int, representative: Genome):
        """
        Initialize a species.
        
        Args:
            species_id: Unique identifier for this species
            representative: Representative genome for this species
        """
        self.id = species_id
        self.representative = representative
        self.members: List[Genome] = []
        self.max_fitness = 0.0
        self.avg_fitness = 0.0
        self.generations_without_improvement = 0
    
    def add_member(self, genome: Genome) -> None:
        """
        Add a genome to this species.
        
        Args:
            genome: Genome to add
        """
        self.members.append(genome)
        genome.species_id = self.id
    
    def update_fitness(self) -> None:
        """Update species fitness statistics."""
        if not self.members:
            self.avg_fitness = 0.0
            return
        
        fitnesses = [g.fitness for g in self.members]
        self.avg_fitness = sum(fitnesses) / len(fitnesses)
        current_max = max(fitnesses)
        
        if current_max > self.max_fitness:
            self.max_fitness = current_max
            self.generations_without_improvement = 0
        else:
            self.generations_without_improvement += 1
    
    def cull_weak_members(self, survival_rate: float = 0.5) -> None:
        """
        Remove weak members from the species.
        
        Args:
            survival_rate: Fraction of members to keep
        """
        if not self.members:
            return
        
        self.members.sort(key=lambda g: g.fitness, reverse=True)
        keep_count = max(1, int(len(self.members) * survival_rate))
        self.members = self.members[:keep_count]
    
    def select_new_representative(self) -> None:
        """Select a new representative genome randomly from members."""
        if self.members:
            self.representative = random.choice(self.members)


class SpeciesManager:
    """Manages all species in the population."""
    
    def __init__(self):
        """Initialize the species manager."""
        self.species: Dict[int, Species] = {}
        self.next_species_id = 0
        self.compatibility_threshold = config.get('evolution.species_divergence_threshold')
    
    def speciate(self, genomes: List[Genome]) -> None:
        """
        Assign genomes to species based on compatibility.
        
        Args:
            genomes: List of genomes to assign to species
        """
        # Clear existing members
        for species in self.species.values():
            species.members.clear()
        
        # Assign each genome to a species
        for genome in genomes:
            assigned = False
            
            for species in self.species.values():
                if self._is_compatible(genome, species.representative):
                    species.add_member(genome)
                    assigned = True
                    break
            
            # Create new species if no compatible species found
            if not assigned:
                new_species = Species(self.next_species_id, genome)
                new_species.add_member(genome)
                self.species[self.next_species_id] = new_species
                self.next_species_id += 1
        
        # Remove empty species
        empty_species = [sid for sid, s in self.species.items() if not s.members]
        for sid in empty_species:
            del self.species[sid]
        
        # Update fitness for all species
        for species in self.species.values():
            species.update_fitness()
    
    def _is_compatible(self, genome1: Genome, genome2: Genome) -> bool:
        """
        Check if two genomes are compatible (similar enough for same species).
        
        Args:
            genome1: First genome
            genome2: Second genome
            
        Returns:
            True if genomes are compatible
        """
        distance = self._calculate_distance(genome1, genome2)
        return distance < self.compatibility_threshold
    
    def _calculate_distance(self, genome1: Genome, genome2: Genome) -> float:
        """
        Calculate genetic distance between two genomes.
        
        This uses a simplified NEAT-style distance calculation based on:
        - Number of excess and disjoint connections
        - Average weight difference of matching connections
        - Difference in network size
        
        Args:
            genome1: First genome
            genome2: Second genome
            
        Returns:
            Genetic distance value
        """
        # Get connection innovations (from_neuron, to_neuron pairs)
        innovations1 = {
            (c.from_neuron, c.to_neuron): c.weight 
            for c in genome1.network.connections
        }
        innovations2 = {
            (c.from_neuron, c.to_neuron): c.weight 
            for c in genome2.network.connections
        }
        
        # Find matching, disjoint, and excess genes
        all_innovations = set(innovations1.keys()) | set(innovations2.keys())
        matching = set(innovations1.keys()) & set(innovations2.keys())
        disjoint_excess = len(all_innovations) - len(matching)
        
        # Calculate average weight difference for matching connections
        weight_diff = 0.0
        if matching:
            weight_diff = sum(
                abs(innovations1[inn] - innovations2[inn]) 
                for inn in matching
            ) / len(matching)
        
        # Calculate difference in network size
        size_diff = abs(
            len(genome1.network.neurons) - len(genome2.network.neurons)
        )
        
        # Coefficients for distance calculation
        c1 = 1.0  # Disjoint/excess coefficient
        c2 = 0.5  # Weight difference coefficient
        c3 = 0.3  # Size difference coefficient
        
        # Normalize by genome size
        N = max(len(innovations1), len(innovations2), 1)
        
        distance = (c1 * disjoint_excess / N + 
                   c2 * weight_diff + 
                   c3 * size_diff)
        
        return distance
    
    def get_species_count(self) -> int:
        """
        Get the number of active species.
        
        Returns:
            Number of species
        """
        return len(self.species)
    
    def get_species_sizes(self) -> Dict[int, int]:
        """
        Get the size of each species.
        
        Returns:
            Dictionary mapping species ID to member count
        """
        return {sid: len(s.members) for sid, s in self.species.items()}
    
    def cull_species(self, stagnation_limit: int = 15) -> None:
        """
        Remove species that have stagnated.
        
        Args:
            stagnation_limit: Number of generations without improvement before culling
        """
        stagnant = [
            sid for sid, s in self.species.items() 
            if s.generations_without_improvement >= stagnation_limit
        ]
        
        # Keep at least one species
        if len(stagnant) < len(self.species):
            for sid in stagnant:
                del self.species[sid]
    
    def adjust_fitness(self) -> None:
        """
        Adjust fitness of all genomes based on species size (fitness sharing).
        
        This prevents any single species from dominating the population.
        """
        for species in self.species.values():
            species_size = len(species.members)
            if species_size > 0:
                for genome in species.members:
                    genome.fitness /= species_size
