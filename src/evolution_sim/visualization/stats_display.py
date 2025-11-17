"""Statistics display for the simulation."""

import pygame
import numpy as np
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..environment.world import Environment
    from ..evolution.evolution_tracker import EvolutionTracker

from .network_visualizer import NetworkVisualizer

class StatsDisplay:
    """Displays simulation statistics with evolutionary tracking."""
    
    def __init__(self, screen: pygame.Surface, tracker: 'EvolutionTracker'):
        """
        Initialize the stats display.
        
        Args:
            screen: Pygame screen to draw on
            tracker: Evolution tracker instance
        """
        self.screen = screen
        self.tracker = tracker
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.frame = 0
        
        # Selected creature for inspection
        self.selected_creature = None
        
        # Clickable areas
        self.oldest_creature_rect = None
        self.oldest_creature = None
        
        self.network_visualizer = NetworkVisualizer()
    
    def update(self, environment: 'Environment') -> None:
        """
        Update and draw statistics.
        
        Args:
            environment: The environment to display stats for
        """
        herbivores = [c for c in environment.creatures if c.creature_type == 'herbivore']
        carnivores = [c for c in environment.creatures if c.creature_type == 'carnivore']
        
        # Find oldest creature
        if environment.creatures:
            self.oldest_creature = max(environment.creatures, key=lambda c: c.age)
        else:
            self.oldest_creature = None
        
        # Main stats
        stats = [
            f"Frame: {self.frame}",
            f"Generation (Max): {self.tracker.max_generation}",
            f"Herbivores: {len(herbivores)}",
            f"Carnivores: {len(carnivores)}",
            f"Plants: {len(environment.plants)}",
            f"Total Births: {self.tracker.total_births}",
            f"Total Deaths: {self.tracker.total_deaths}",
            ""
        ]
        
        # Average stats
        if herbivores:
            avg_age_h = np.mean([c.age for c in herbivores])
            avg_neurons_h = np.mean([len(c.genome.network.neurons) for c in herbivores])
            avg_gen_h = np.mean([c.generation for c in herbivores])
            stats.append(f"Herbivore Avg Age: {avg_age_h:.0f}")
            stats.append(f"Herbivore Avg Gen: {avg_gen_h:.1f}")
            stats.append(f"Herbivore Neurons: {avg_neurons_h:.1f}")
        
        if carnivores:
            avg_age_c = np.mean([c.age for c in carnivores])
            avg_neurons_c = np.mean([len(c.genome.network.neurons) for c in carnivores])
            stats.append(f"Carnivore Avg Age: {avg_age_c:.0f}")
            stats.append(f"Carnivore Neurons: {avg_neurons_c:.1f}")
        
        self._draw_stats(stats, 10, 10)
        
        # Draw clickable oldest creature box
        self._draw_oldest_creature_box()
        
        # Draw all-time bests
        self._draw_best_performers(environment.creatures)
        
        # Draw selected creature info
        if self.selected_creature and self.selected_creature.alive:
            self._draw_creature_info(self.selected_creature)
            
            # ADD THIS: Draw neural network visualization
            self._draw_selected_network()
        
        self.frame += 1
    
    def _draw_selected_network(self) -> None:
        """Draw the neural network of the selected creature."""
        if not self.selected_creature or not self.selected_creature.alive:
            return
        
        # Position in top-right area
        screen_width = self.screen.get_width()
        x = screen_width - 450
        y = 280
        width = 430
        height = 350
        
        self.network_visualizer.draw_network(
            self.screen,
            self.selected_creature.genome.network,
            x, y, width, height
        )

    
    def _draw_oldest_creature_box(self) -> None:
        """Draw clickable box showing the oldest creature."""
        if not self.oldest_creature:
            return
        
        x = 10
        y = 350
        width = 300
        height = 100
        
        # Store rect for click detection
        self.oldest_creature_rect = pygame.Rect(x, y, width, height)
        
        # Draw background (highlight if selected)
        is_selected = (self.selected_creature == self.oldest_creature)
        bg_color = (60, 80, 60) if is_selected else (60, 60, 80)
        s = pygame.Surface((width, height))
        s.set_alpha(200)
        s.fill(bg_color)
        self.screen.blit(s, (x, y))
        
        # Draw border (yellow if selected, white otherwise)
        border_color = (255, 255, 0) if is_selected else (150, 150, 200)
        pygame.draw.rect(self.screen, border_color, self.oldest_creature_rect, 2)
        
        # Draw title
        title = self.font.render("OLDEST ALIVE (Click to Follow)", True, (100, 255, 100))
        self.screen.blit(title, (x + 10, y + 5))
        
        # Draw creature info
        c = self.oldest_creature
        type_color = (100, 200, 255) if c.creature_type == 'herbivore' else (255, 100, 100)
        
        lines = [
            f"ID #{c.id} ({c.creature_type.capitalize()})",
            f"Age: {c.age} frames | Gen: {c.generation}",
            f"Energy: {c.energy:.1f} | Food: {c.food_eaten}",
        ]
        
        y_offset = y + 32
        for line in lines:
            text = self.small_font.render(line, True, type_color)
            self.screen.blit(text, (x + 15, y_offset))
            y_offset += 20
    
    def _draw_stats(self, stats: list, x: int, y: int) -> None:
        """Draw statistics text on screen."""
        y_offset = y
        for stat in stats:
            text = self.font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (x, y_offset))
            y_offset += 25
    
    def _draw_best_performers(self, current_creatures) -> None:
        """Draw all-time best performers."""
        x = self.screen.get_width() - 350
        y = 10
        
        # Draw panel background
        panel_height = 250
        s = pygame.Surface((340, panel_height))
        s.set_alpha(180)
        s.fill((40, 40, 40))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, 340, panel_height), 2)
        
        # Title
        title = self.font.render("All-Time Best", True, (255, 215, 0))
        self.screen.blit(title, (x + 10, y + 5))
        
        y_offset = y + 35
        
        # Best herbivore
        if self.tracker.best_herbivore:
            h = self.tracker.best_herbivore
            lines = [
                "Best Herbivore:",
                f"  ID #{h.id} | Gen {h.generation}",
                f"  Fitness: {h.fitness:.1f} | Lived: {h.lifespan} frames",
                f"  Food: {h.food_eaten} | Children: {h.children_count}",
            ]
            for line in lines:
                text = self.small_font.render(line, True, (100, 200, 255))
                self.screen.blit(text, (x + 10, y_offset))
                y_offset += 20
        
        y_offset += 10
        
        # Best carnivore
        if self.tracker.best_carnivore:
            c = self.tracker.best_carnivore
            lines = [
                "Best Carnivore:",
                f"  ID #{c.id} | Gen {c.generation}",
                f"  Fitness: {c.fitness:.1f} | Lived: {c.lifespan} frames",
                f"  Kills: {c.food_eaten} | Children: {c.children_count}",
            ]
            for line in lines:
                text = self.small_font.render(line, True, (255, 100, 100))
                self.screen.blit(text, (x + 10, y_offset))
                y_offset += 20
        
        y_offset += 10
        
        # Longest lived
        if self.tracker.longest_lived:
            l = self.tracker.longest_lived
            type_color = (100, 200, 255) if l.type == 'herbivore' else (255, 100, 100)
            text = self.small_font.render(f"Longest Lived: #{l.id} ({l.lifespan} frames)", True, type_color)
            self.screen.blit(text, (x + 10, y_offset))
    
    def _draw_creature_info(self, creature) -> None:
        """Draw detailed info about selected creature."""
        x = 10
        y = self.screen.get_height() - 250
        width = 400
        height = 240
        
        # Draw panel background
        s = pygame.Surface((width, height))
        s.set_alpha(200)
        s.fill((40, 40, 60))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, (255, 255, 0), (x, y, width, height), 3)
        
        # Creature info
        color = (100, 200, 255) if creature.creature_type == 'herbivore' else (255, 100, 100)
        title = self.font.render(f"Creature #{creature.id} (SELECTED)", True, color)
        self.screen.blit(title, (x + 10, y + 5))
        
        lines = [
            f"Type: {creature.creature_type.capitalize()}",
            f"Generation: {creature.generation}",
            f"Age: {creature.age} frames",
            f"Energy: {creature.energy:.1f}",
            f"Food Eaten: {creature.food_eaten}",
            f"Children: {creature.children_count}",
            f"Fitness: {creature.genome.fitness:.1f}",
            f"Neurons: {len(creature.genome.network.neurons)}",
            f"Connections: {len(creature.genome.network.connections)}",
        ]
        
        if creature.parent_id is not None:
            lines.append(f"Parent ID: #{creature.parent_id}")
        
        y_offset = y + 35
        for line in lines:
            text = self.small_font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (x + 15, y_offset))
            y_offset += 20
    
    def handle_click(self, pos) -> bool:
        """
        Handle mouse click on stats display.
        
        Args:
            pos: Mouse position (x, y)
            
        Returns:
            True if click was handled
        """
        if self.oldest_creature_rect and self.oldest_creature_rect.collidepoint(pos):
            self.select_creature(self.oldest_creature)
            return True
        return False
    
    def select_creature(self, creature) -> None:
        """Select a creature for detailed inspection."""
        self.selected_creature = creature
