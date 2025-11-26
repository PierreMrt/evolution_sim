"""Left panel statistics display."""

import pygame
import numpy as np
import logging
from typing import TYPE_CHECKING
from ..config import config
from .ui import ToggleButton

if TYPE_CHECKING:
    from ..environment.world import Environment
    from ..evolution.evolution_tracker import EvolutionTracker

logger = logging.getLogger(__name__)

class LeftPanel:
    """Displays population stats and all-time bests on the left side."""
    
    def __init__(self, screen: pygame.Surface, tracker: 'EvolutionTracker'):
        """Initialize the left panel."""
        self.screen = screen
        self.tracker = tracker
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Panel dimensions
        self.panel_x = config.get('display.left_panel_x', 0)
        self.panel_width = config.get('display.left_panel_width', 350)
        self.panel_height = screen.get_height()
        
        # Add FOV toggle button
        self.fov_toggle = ToggleButton(
            x=self.panel_x + 20,
            y=self.panel_height - 50,
            size=20,
            label="Show FOV",
            initial_state=config.get('display.show_vision_cones', False),
            callback=self._toggle_fov
        )
        
        self.show_fov = self.fov_toggle.state
    
    def draw(self, environment: 'Environment', frame: int) -> None:
        """Draw left panel contents."""
        # Background
        panel_surface = pygame.Surface((self.panel_width, self.panel_height))
        panel_surface.fill((25, 25, 35))
        self.screen.blit(panel_surface, (self.panel_x, 0))
        
        y_position = 10
        
        # Title
        title = self.font.render("EVOLUTION STATS", True, (150, 200, 255))
        self.screen.blit(title, (self.panel_x + 20, y_position))
        y_position += 30
        
        # Frame counter
        text = self.small_font.render(f"Frame: {frame}", True, (180, 180, 180))
        self.screen.blit(text, (self.panel_x + 20, y_position))
        y_position += 20
        
        # Thin separator
        pygame.draw.line(self.screen, (70, 70, 70),
                        (self.panel_x + 20, y_position),
                        (self.panel_x + self.panel_width - 20, y_position), 1)
        y_position += 10
        
        # Population stats (compact)
        y_position = self._draw_population_stats_compact(environment, y_position)
        
        # Thin separator
        y_position += 5
        pygame.draw.line(self.screen, (70, 70, 70),
                        (self.panel_x + 20, y_position),
                        (self.panel_x + self.panel_width - 20, y_position), 1)
        y_position += 10
        
        # All-time bests (compact)
        y_position = self._draw_all_time_bests_compact(y_position)
        
        # Controls at bottom if space
        if y_position < self.panel_height - 100:
            y_position += 20
            pygame.draw.line(self.screen, (70, 70, 70),
                            (self.panel_x + 20, y_position),
                            (self.panel_x + self.panel_width - 20, y_position), 1)
            y_position += 15
            self._draw_controls(y_position)
        
        # Update and draw FOV toggle
        mouse_pos = pygame.mouse.get_pos()
        self.fov_toggle.update(mouse_pos)
        self.fov_toggle.draw(self.screen)
        
        # Border
        pygame.draw.line(self.screen, (100, 100, 100),
                        (self.panel_x + self.panel_width - 1, 0),
                        (self.panel_x + self.panel_width - 1, self.panel_height), 2)
    
    def _draw_population_stats_compact(self, environment, start_y: int) -> int:
        """Draw compact population statistics."""
        x = self.panel_x + 20
        y = start_y
        
        herbivores = [c for c in environment.creatures if c.creature_type == 'herbivore']
        carnivores = [c for c in environment.creatures if c.creature_type == 'carnivore']
        
        # Section title
        title = self.small_font.render("Population", True, (100, 255, 150))
        self.screen.blit(title, (x, y))
        y += 20
        
        # Compact counts
        text = self.small_font.render(
            f"Herbivores: {len(herbivores)} | Carnivores: {len(carnivores)}", 
            True, (180, 180, 180)
        )
        self.screen.blit(text, (x, y))
        y += 18
        
        text = self.small_font.render(f"Plants: {len(environment.plants)}", True, (50, 200, 50))
        self.screen.blit(text, (x, y))
        y += 18
        
        text = self.small_font.render(
            f"Gen: {self.tracker.max_generation} | Births: {self.tracker.total_births} | Deaths: {self.tracker.total_deaths}", 
            True, (180, 180, 180)
        )
        self.screen.blit(text, (x, y))
        y += 22
        
        # HERBIVORE AVERAGES (compact)
        if herbivores:
            avg_age_h = np.mean([c.age for c in herbivores])
            avg_neurons_h = np.mean([len(c.genome.network.neurons) for c in herbivores])
            avg_fitness_h = np.mean([c.genome.fitness for c in herbivores])
            
            text = self.small_font.render("Herbivore Averages:", True, (100, 200, 255))
            self.screen.blit(text, (x, y))
            y += 18
            
            text = self.small_font.render(
                f"  Age: {avg_age_h:.0f} | Neurons: {avg_neurons_h:.1f}", 
                True, (150, 150, 150)
            )
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(f"  Fitness: {avg_fitness_h:.1f}", True, (150, 150, 150))
            self.screen.blit(text, (x, y))
            y += 20
        
        # CARNIVORE AVERAGES (compact)
        if carnivores:
            avg_age_c = np.mean([c.age for c in carnivores])
            avg_neurons_c = np.mean([len(c.genome.network.neurons) for c in carnivores])
            avg_fitness_c = np.mean([c.genome.fitness for c in carnivores])
            
            text = self.small_font.render("Carnivore Averages:", True, (255, 100, 100))
            self.screen.blit(text, (x, y))
            y += 18
            
            text = self.small_font.render(
                f"  Age: {avg_age_c:.0f} | Neurons: {avg_neurons_c:.1f}", 
                True, (150, 150, 150)
            )
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(f"  Fitness: {avg_fitness_c:.1f}", True, (150, 150, 150))
            self.screen.blit(text, (x, y))
            y += 18
        
        return y
    
    def _draw_all_time_bests_compact(self, start_y: int) -> int:
        """Draw compact all-time best performers."""
        x = self.panel_x + 20
        y = start_y
        
        # Section title
        title = self.small_font.render("All-Time Best", True, (255, 215, 0))
        self.screen.blit(title, (x, y))
        y += 20
        
        # Best Herbivore (compact)
        if self.tracker.best_herbivore:
            h = self.tracker.best_herbivore
            text = self.small_font.render(f"Herbivore: #{h.id} (Gen {h.generation})", True, (100, 200, 255))
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(
                f"  Fitness: {h.fitness:.0f} | Lived: {h.lifespan}", 
                True, (140, 140, 140)
            )
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(f"  Food: {h.food_eaten}", True, (140, 140, 140))
            self.screen.blit(text, (x, y))
            y += 20
        
        # Best Carnivore (compact)
        if self.tracker.best_carnivore:
            c = self.tracker.best_carnivore
            text = self.small_font.render(f"Carnivore: #{c.id} (Gen {c.generation})", True, (255, 100, 100))
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(
                f"  Fitness: {c.fitness:.0f} | Lived: {c.lifespan}", 
                True, (140, 140, 140)
            )
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(f"  Kills: {c.food_eaten}", True, (140, 140, 140))
            self.screen.blit(text, (x, y))
            y += 20
        
        # Longest Lived (compact)
        if self.tracker.longest_lived:
            l = self.tracker.longest_lived
            type_color = (100, 200, 255) if l.type == 'herbivore' else (255, 100, 100)
            text = self.small_font.render(f"Longest Lived: #{l.id}", True, (200, 200, 200))
            self.screen.blit(text, (x, y))
            y += 16
            
            text = self.small_font.render(f"  {l.type.capitalize()} | {l.lifespan} frames", True, type_color)
            self.screen.blit(text, (x, y))
            y += 18
        
        return y
    
    def _toggle_fov(self, state: bool) -> None:
        """Callback for FOV toggle."""
        self.show_fov = state
        logger.info(f"Vision cones: {'ON' if state else 'OFF'}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks on the panel."""
        return self.fov_toggle.handle_event(event)
    
    def _draw_controls(self, start_y: int) -> None:
        """Draw control instructions."""
        x = self.panel_x + 20
        y = start_y
        
        # Section title
        title = self.small_font.render("Controls", True, (150, 200, 255))
        self.screen.blit(title, (x, y))
        y += 20
        
        # Instructions
        instructions = [
            "Click creature to select",
            "SPACE: Pause/Resume",
        ]
        
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (150, 150, 150))
            self.screen.blit(text, (x, y))
            y += 16
