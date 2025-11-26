"""Main rendering engine for the simulation."""

import pygame
import math
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
    
    def draw(self, environment: 'Environment', selected_creature=None, show_vision: bool = True) -> None:
        """
        Render the current simulation state.
        
        Args:
            environment: The environment to render
            selected_creature: Currently selected creature
            show_vision: Whether to display vision cones
        """
        # Clear main screen with dark background
        self.screen.fill((30, 30, 30))
        
        # Draw world on separate surface
        self.world_surface.fill((20, 30, 20))  # Dark green background for world
        self._draw_plants(environment)
        self._draw_creatures(environment, selected_creature, show_vision)
        
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
    
    def _draw_creatures(self, environment: 'Environment', selected_creature=None, show_vision: bool = True) -> None:
        """Draw all creatures with energy bars, vision cones, and direction indicators."""
        max_energy = config.get('creatures.max_energy')
        
        for creature in environment.creatures:
            if creature.alive:
                # Draw vision cone first (behind creature)
                # Always show for selected creature, or if vision is toggled on
                if show_vision or creature == selected_creature:
                    self._draw_vision_cone(creature)
                
                # Determine color
                if creature == selected_creature:
                    color = (255, 255, 0)  # Yellow for selected
                elif creature.creature_type == 'herbivore':
                    color = (100, 150, 255)
                else:
                    color = (255, 100, 100)
                
                # Draw creature body
                pygame.draw.circle(
                    self.world_surface,
                    color,
                    (int(creature.x), int(creature.y)),
                    creature.radius
                )
                
                # Draw direction indicator (triangle or line)
                self._draw_direction_indicator(creature, color)
                
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
    
    def _draw_vision_cone(self, creature) -> None:
        """Draw semi-transparent vision cone for a creature."""
        vision_angle = math.radians(config.get('creatures.vision_angle', 120))
        vision_range = config.get('creatures.vision_range', 150)
        alpha = config.get('display.vision_cone_alpha', 40)
        
        # Create temporary surface with per-pixel alpha
        vision_surface = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)
        
        # Calculate vision cone color based on creature type
        if creature.creature_type == 'herbivore':
            cone_color = (100, 150, 255, alpha)
        else:
            cone_color = (255, 100, 100, alpha)
        
        # Calculate cone vertices
        start_angle = creature.direction - vision_angle / 2
        end_angle = creature.direction + vision_angle / 2
        
        # Build polygon points for the vision cone
        points = [(int(creature.x), int(creature.y))]
        
        # Add arc points
        num_segments = 20
        for i in range(num_segments + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_segments
            px = creature.x + vision_range * math.cos(angle)
            py = creature.y + vision_range * math.sin(angle)
            points.append((int(px), int(py)))
        
        # Draw the vision cone
        if len(points) > 2:
            pygame.draw.polygon(vision_surface, cone_color, points)
        
        # Blit the vision surface onto the world surface
        self.world_surface.blit(vision_surface, (0, 0))
    
    def _draw_direction_indicator(self, creature, color) -> None:
        """Draw a triangle or arrow showing which direction creature is facing."""
        # Draw a small triangle pointing in the direction
        triangle_size = creature.radius * 0.6
        
        # Calculate triangle points
        tip_x = creature.x + creature.radius * 0.8 * math.cos(creature.direction)
        tip_y = creature.y + creature.radius * 0.8 * math.sin(creature.direction)
        
        # Two base points perpendicular to direction
        perp_angle_1 = creature.direction + 2.5
        perp_angle_2 = creature.direction - 2.5
        
        base1_x = creature.x + triangle_size * math.cos(perp_angle_1)
        base1_y = creature.y + triangle_size * math.sin(perp_angle_1)
        
        base2_x = creature.x + triangle_size * math.cos(perp_angle_2)
        base2_y = creature.y + triangle_size * math.sin(perp_angle_2)
        
        # Draw filled triangle
        points = [
            (int(tip_x), int(tip_y)),
            (int(base1_x), int(base1_y)),
            (int(base2_x), int(base2_y))
        ]
        
        # Use darker shade for the direction indicator
        indicator_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.polygon(self.world_surface, indicator_color, points)
    
    def get_world_rect(self):
        """Return the rectangle representing the world area."""
        return pygame.Rect(self.world_x, self.world_y, self.world_width, self.world_height)
