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
        
        # Window dimensions
        self.window_width = config.get('display.window_width', 1600)
        self.window_height = config.get('display.window_height', 900)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Neural Evolution Ecosystem")
        
        # World viewport dimensions
        self.world_x = config.get('display.world_x', 0)
        self.world_y = config.get('display.world_y', 0)
        self.world_width = config.get('display.world_viewport_width', 1200)
        self.world_height = config.get('display.world_viewport_height', 900)
        
        # Create a surface for the world
        self.world_surface = pygame.Surface((self.world_width, self.world_height))
    
    def draw(self, environment: 'Environment', selected_creature=None) -> None:
        """
        Render the current simulation state.
        
        Args:
            environment: The environment to render
            selected_creature: Currently selected creature
        """
        # Clear main screen with dark background
        self.screen.fill((30, 30, 30))
        
        # Draw world on separate surface
        self.world_surface.fill((20, 30, 20))  # Dark green background for world
        self._draw_plants(environment)
        self._draw_creatures(environment, selected_creature)
        
        # Blit world surface to main screen
        self.screen.blit(self.world_surface, (self.world_x, self.world_y))
        
        # Draw border around world
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (self.world_x, self.world_y, self.world_width, self.world_height), 2)
    
    def _draw_plants(self, environment: 'Environment') -> None:
        """Draw all plants on the world surface."""
        for plant in environment.plants:
            pygame.draw.circle(
                self.world_surface,
                (50, 200, 50),
                (int(plant[0]), int(plant[1])),
                3
            )
    
    def _draw_creatures(self, environment: 'Environment', selected_creature=None) -> None:
        """Draw all creatures with energy bars on the world surface."""
        max_energy = config.get('creatures.max_energy')
        
        for creature in environment.creatures:
            if creature.alive:
                # Determine color
                if creature == selected_creature:
                    color = (255, 255, 0)  # Yellow for selected
                elif creature.creature_type == 'herbivore':
                    color = (100, 150, 255)
                else:
                    color = (255, 100, 100)
                
                # Draw creature
                pygame.draw.circle(
                    self.world_surface,
                    color,
                    (int(creature.x), int(creature.y)),
                    creature.radius
                )
                
                # Draw selection ring
                if creature == selected_creature:
                    pygame.draw.circle(
                        self.world_surface,
                        (255, 255, 0),
                        (int(creature.x), int(creature.y)),
                        creature.radius + 5,
                        2
                    )
                
                # Draw energy bar
                energy_ratio = creature.energy / max_energy
                bar_width = creature.radius * 2
                bar_height = 3
                bar_x = creature.x - creature.radius
                bar_y = creature.y - creature.radius - 5
                
                pygame.draw.rect(
                    self.world_surface,
                    (100, 100, 100),
                    (bar_x, bar_y, bar_width, bar_height)
                )
                
                pygame.draw.rect(
                    self.world_surface,
                    (0, 255, 0),
                    (bar_x, bar_y, bar_width * energy_ratio, bar_height)
                )
    
    def get_world_rect(self):
        """Return the rectangle representing the world area."""
        return pygame.Rect(self.world_x, self.world_y, self.world_width, self.world_height)
