"""Statistics display for the simulation."""
import pygame
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..environment.world import Environment


class StatsDisplay:
    """Displays simulation statistics."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the stats display.
        
        Args:
            screen: Pygame screen to draw on
        """
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.frame = 0
    
    def update(self, environment: 'Environment') -> None:
        """
        Update and draw statistics.
        
        Args:
            environment: The environment to display stats for
        """
        herbivores = [c for c in environment.creatures if c.creature_type == 'herbivore']
        carnivores = [c for c in environment.creatures if c.creature_type == 'carnivore']
        
        stats = [
            f"Frame: {self.frame}",
            f"Herbivores: {len(herbivores)}",
            f"Carnivores: {len(carnivores)}",
            f"Plants: {len(environment.plants)}",
            f"Total Creatures: {len(environment.creatures)}",
        ]
        
        if herbivores:
            avg_neurons_h = np.mean([len(c.genome.network.neurons) for c in herbivores])
            stats.append(f"Avg Herbivore Neurons: {avg_neurons_h:.1f}")
        
        if carnivores:
            avg_neurons_c = np.mean([len(c.genome.network.neurons) for c in carnivores])
            stats.append(f"Avg Carnivore Neurons: {avg_neurons_c:.1f}")
        
        stats.append("SPACE: Pause/Resume")
        
        self._draw_stats(stats)
        self.frame += 1
    
    def _draw_stats(self, stats: list) -> None:
        """Draw statistics text on screen."""
        y_offset = 10
        for stat in stats:
            text = self.font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
