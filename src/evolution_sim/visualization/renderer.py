"""Main rendering engine for the simulation."""

import pygame
from typing import TYPE_CHECKING
from ..config import config

if TYPE_CHECKING:
    from ..environment.world import Environment


class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self):
        """Initialize the renderer."""
        pygame.init()
        width = config.get('display.window_width')
        height = config.get('display.window_height')
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Neural Evolution Ecosystem")
        
    def draw(self, environment: 'Environment') -> None:
        """
        Render the current simulation state.
        
        Args:
            environment: The environment to render
        """
        self.screen.fill((20, 30, 20))  # Dark green background
        
        self._draw_plants(environment)
        self._draw_creatures(environment)
    
    def _draw_plants(self, environment: 'Environment') -> None:
        """Draw all plants."""
        for plant in environment.plants:
            pygame.draw.circle(
                self.screen, 
                (50, 200, 50), 
                (int(plant[0]), int(plant[1])), 
                3
            )
    
    def _draw_creatures(self, environment: 'Environment') -> None:
        """Draw all creatures with energy bars."""
        max_energy = config.get('creatures.max_energy')
        
        for creature in environment.creatures:
            if creature.alive:
                # Determine color
                color = (100, 150, 255) if creature.creature_type == 'herbivore' else (255, 100, 100)
                
                # Draw creature
                pygame.draw.circle(
                    self.screen, 
                    color, 
                    (int(creature.x), int(creature.y)), 
                    creature.radius
                )
                
                # Draw energy bar
                energy_ratio = creature.energy / max_energy
                bar_width = creature.radius * 2
                bar_height = 3
                bar_x = creature.x - creature.radius
                bar_y = creature.y - creature.radius - 5
                
                pygame.draw.rect(
                    self.screen, 
                    (100, 100, 100), 
                    (bar_x, bar_y, bar_width, bar_height)
                )
                pygame.draw.rect(
                    self.screen, 
                    (0, 255, 0), 
                    (bar_x, bar_y, bar_width * energy_ratio, bar_height)
                )
