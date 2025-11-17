"""Selection algorithms for evolutionary processes."""
import random
from typing import List, Tuple
from ..core.genome import Genome


class SelectionEngine:
    """Handles selection of genomes for reproduction."""
    
    @staticmethod
    def tournament_selection(
        genomes: List[Genome], 
        tournament_size: int = 3
    ) -> Genome:
        """
        Select a genome using tournament selection.
        
        Args:
            genomes: Population of genomes
            tournament_size: Number of individuals in tournament
            
        Returns:
            Selected genome
        """
        tournament = random.sample(genomes, min(tournament_size, len(genomes)))
        return max(tournament, key=lambda g: g.fitness)
    
    @staticmethod
    def roulette_wheel_selection(genomes: List[Genome]) -> Genome:
        """
        Select a genome using fitness-proportionate selection.
        
        Args:
            genomes: Population of genomes
            
        Returns:
            Selected genome
        """
        # Shift fitness to ensure all values are positive
        min_fitness = min(g.fitness for g in genomes)
        if min_fitness < 0:
            adjusted_fitnesses = [g.fitness - min_fitness + 1 for g in genomes]
        else:
            adjusted_fitnesses = [g.fitness for g in genomes]
        
        total_fitness = sum(adjusted_fitnesses)
        
        if total_fitness == 0:
            return random.choice(genomes)
        
        # Spin the wheel
        pick = random.uniform(0, total_fitness)
        current = 0
        
        for genome, fitness in zip(genomes, adjusted_fitnesses):
            current += fitness
            if current >= pick:
                return genome
        
        return genomes[-1]
    
    @staticmethod
    def rank_selection(genomes: List[Genome]) -> Genome:
        """
        Select a genome using rank-based selection.
        
        Args:
            genomes: Population of genomes
            
        Returns:
            Selected genome
        """
        # Sort by fitness
        sorted_genomes = sorted(genomes, key=lambda g: g.fitness)
        
        # Assign ranks (1 to n)
        ranks = list(range(1, len(sorted_genomes) + 1))
        total_rank = sum(ranks)
        
        # Select based on rank
        pick = random.uniform(0, total_rank)
        current = 0
        
        for genome, rank in zip(sorted_genomes, ranks):
            current += rank
            if current >= pick:
                return genome
        
        return sorted_genomes[-1]
    
    @staticmethod
    def elitism_selection(
        genomes: List[Genome], 
        elite_count: int = 2
    ) -> List[Genome]:
        """
        Select the top performing genomes.
        
        Args:
            genomes: Population of genomes
            elite_count: Number of elite individuals to select
            
        Returns:
            List of elite genomes
        """
        sorted_genomes = sorted(genomes, key=lambda g: g.fitness, reverse=True)
        return sorted_genomes[:elite_count]
    
    @staticmethod
    def select_parents(
        genomes: List[Genome], 
        method: str = 'tournament'
    ) -> Tuple[Genome, Genome]:
        """
        Select two parents for reproduction.
        
        Args:
            genomes: Population of genomes
            method: Selection method ('tournament', 'roulette', 'rank')
            
        Returns:
            Tuple of two parent genomes
        """
        if method == 'tournament':
            parent1 = SelectionEngine.tournament_selection(genomes)
            parent2 = SelectionEngine.tournament_selection(genomes)
        elif method == 'roulette':
            parent1 = SelectionEngine.roulette_wheel_selection(genomes)
            parent2 = SelectionEngine.roulette_wheel_selection(genomes)
        elif method == 'rank':
            parent1 = SelectionEngine.rank_selection(genomes)
            parent2 = SelectionEngine.rank_selection(genomes)
        else:
            parent1 = random.choice(genomes)
            parent2 = random.choice(genomes)
        
        return parent1, parent2
