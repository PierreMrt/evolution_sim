"""Right panel for selected creature details."""

import pygame
from typing import TYPE_CHECKING, Optional
from ..config import config

if TYPE_CHECKING:
    from ..environment.world import Environment

from .network_visualizer import NetworkVisualizer

class RightPanel:
    """Displays selected creature details and neural network."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the right panel."""
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Panel dimensions
        self.panel_x = config.get('display.right_panel_x', 1570)
        self.panel_width = config.get('display.right_panel_width', 350)
        self.panel_height = screen.get_height()
        
        self.selected_creature = None
        self.oldest_creature = None
        self.oldest_creature_rect = None
        
        self.network_visualizer = NetworkVisualizer()
    
    def draw(self, environment: 'Environment') -> None:
        """Draw right panel contents."""
        # Background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.fill((25, 25, 35))
        self.screen.blit(panel_surface, (self.panel_x, 0))
        
        # Find oldest
        if environment.creatures:
            self.oldest_creature = max(environment.creatures, key=lambda c: c.age)
        else:
            self.oldest_creature = None
        
        y_position = 20
        
        # Oldest creature (clickable)
        y_position = self._draw_oldest_creature(y_position)
        
        # Selected creature details
        if self.selected_creature and self.selected_creature.alive:
            y_position += 10
            y_position = self._draw_selected_creature(y_position)
            
            # Neural network at bottom
            self._draw_neural_network()
        
        # Border
        pygame.draw.line(self.screen, (100, 100, 100),
                        (self.panel_x, 0),
                        (self.panel_x, self.panel_height), 2)
    
    def _draw_oldest_creature(self, start_y: int) -> int:
        """Draw oldest creature box."""
        if not self.oldest_creature:
            return start_y
        
        x = self.panel_x + 15
        y = start_y
        width = self.panel_width - 30
        height = 95
        
        self.oldest_creature_rect = pygame.Rect(x, y, width, height)
        
        # Background
        is_selected = (self.selected_creature == self.oldest_creature)
        bg_color = (50, 70, 50) if is_selected else (50, 50, 70)
        pygame.draw.rect(self.screen, bg_color, self.oldest_creature_rect)
        
        # Border
        border_color = (255, 255, 0) if is_selected else (100, 100, 150)
        pygame.draw.rect(self.screen, border_color, self.oldest_creature_rect, 2)
        
        # Title
        title = self.font.render("OLDEST ALIVE", True, (100, 255, 100))
        self.screen.blit(title, (x + 10, y + 8))
        
        subtitle = self.small_font.render("(Click to Follow)", True, (150, 150, 150))
        self.screen.blit(subtitle, (x + 10, y + 28))
        
        # Info
        c = self.oldest_creature
        type_color = (100, 200, 255) if c.creature_type == 'herbivore' else (255, 100, 100)
        
        text = self.small_font.render(
            f"ID #{c.id} ({c.creature_type.capitalize()}) | Gen: {c.generation}", 
            True, type_color
        )
        self.screen.blit(text, (x + 10, y + 52))
        
        text = self.small_font.render(
            f"Age: {c.age} | Energy: {c.energy:.1f} | Food: {c.food_eaten}", 
            True, (200, 200, 200)
        )
        self.screen.blit(text, (x + 10, y + 72))
        
        return y + height
    
    def _draw_selected_creature(self, start_y: int) -> int:
        """Draw selected creature details."""
        x = self.panel_x + 15
        y = start_y
        width = self.panel_width - 30
        
        # Background box
        height = 230
        pygame.draw.rect(self.screen, (40, 40, 60), (x, y, width, height))
        pygame.draw.rect(self.screen, (255, 255, 0), (x, y, width, height), 2)
        
        # Title
        title = self.font.render("SELECTED", True, (255, 255, 0))
        self.screen.blit(title, (x + 10, y + 8))
        y += 32
        
        c = self.selected_creature
        color = (100, 200, 255) if c.creature_type == 'herbivore' else (255, 100, 100)
        
        # Creature ID
        text = self.small_font.render(f"Creature #{c.id}", True, color)
        self.screen.blit(text, (x + 10, y))
        y += 22
        
        # Stats (compact)
        stats = [
            f"Type: {c.creature_type.capitalize()}",
            f"Generation: {c.generation}",
            f"Age: {c.age} frames",
            f"Energy: {c.energy:.1f}",
            f"Food: {c.food_eaten} | Children: {c.children_count}",
            f"Fitness: {c.genome.fitness:.1f}",
            "",
            f"Network:",
            f"  {len(c.genome.network.neurons)} neurons",
            f"  {len(c.genome.network.connections)} connections",
        ]
        
        for stat in stats:
            if stat:
                text = self.small_font.render(stat, True, (200, 200, 200))
                self.screen.blit(text, (x + 10, y))
            y += 16
        
        return start_y + height
    
    def _draw_neural_network(self) -> None:
        """Draw neural network at bottom."""
        if not self.selected_creature or not self.selected_creature.alive:
            return
        
        x = self.panel_x + 15
        y = self.panel_height - 450
        width = self.panel_width - 30
        height = 430
        
        # Background
        pygame.draw.rect(self.screen, (30, 30, 40), (x, y, width, height))
        pygame.draw.rect(self.screen, (100, 100, 150), (x, y, width, height), 1)
        
        # Title
        title = self.small_font.render("Neural Network", True, (200, 200, 255))
        self.screen.blit(title, (x + 5, y + 5))
        
        self.network_visualizer.draw_network(
            self.screen,
            self.selected_creature.genome.network,
            x, y + 25, width, height - 30
        )
    
    def select_creature(self, creature) -> None:
        """Select a creature."""
        self.selected_creature = creature
    
    def handle_click(self, pos) -> bool:
        """Handle mouse click."""
        if self.oldest_creature_rect and self.oldest_creature_rect.collidepoint(pos):
            self.select_creature(self.oldest_creature)
            return True
        return False
