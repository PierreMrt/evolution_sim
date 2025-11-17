"""Main simulation entry point."""

import pygame
import math
from evolution_sim.environment.world import Environment
from evolution_sim.visualization.renderer import Renderer
from evolution_sim.visualization.stats_display import StatsDisplay
from evolution_sim.evolution.evolution_tracker import EvolutionTracker  # ADD THIS IMPORT
from evolution_sim.config import config

class Simulation:
    """Main simulation controller."""
    
    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer()
        
        # CREATE TRACKER FIRST
        self.tracker = EvolutionTracker()
        
        # Pass tracker to stats display
        self.stats_display = StatsDisplay(self.renderer.screen, self.tracker)
        
        self.environment = Environment()
        
        # Register initial population
        for creature in self.environment.creatures:
            self.tracker.register_birth(creature)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.selected_creature = None  # For clicking creatures
    
    def handle_events(self) -> None:
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    
                    # Check if click was on stats display first
                    if self.stats_display.handle_click(event.pos):
                        # Stats handled the click
                        self.selected_creature = self.stats_display.selected_creature
                    else:
                        # Try to select creature at mouse position
                        self._select_creature_at(mouse_x, mouse_y)

    
    def _select_creature_at(self, x: int, y: int) -> None:
        """Select a creature at the given position."""
        for creature in self.environment.creatures:
            if creature.alive:
                dist = math.sqrt((creature.x - x)**2 + (creature.y - y)**2)
                if dist < creature.radius + 5:
                    self.selected_creature = creature
                    self.stats_display.select_creature(creature)
                    return
        # If no creature clicked, deselect
        self.selected_creature = None
        self.stats_display.select_creature(None)
    
    def update(self) -> None:
        """Update simulation state."""
        if not self.paused:
            # Store creatures that are alive before update
            alive_before = set(c.id for c in self.environment.creatures if c.alive)
            
            # Update environment (includes reproduction)
            self.environment.update()
            
            # Register deaths
            if hasattr(self.environment, 'dead_this_frame'):
                for dead_creature in self.environment.dead_this_frame:
                    self.tracker.register_death(dead_creature)
                self.environment.dead_this_frame = []
            
            # Register new births
            for creature in self.environment.creatures:
                if creature.id not in alive_before:
                    self.tracker.register_birth(creature)
            
            # Check if selected creature died
            if self.selected_creature and not self.selected_creature.alive:
                self.selected_creature = None
                self.stats_display.select_creature(None)
            
            # Update tracker statistics
            self.tracker.update(self.environment)

    
    def render(self) -> None:
        """Render simulation."""
        # Pass selected creature to renderer
        self.renderer.draw(self.environment, self.selected_creature)
        self.stats_display.update(self.environment)
        pygame.display.flip()
    
    def run(self) -> None:
        """Main simulation loop."""
        fps = config.get('display.fps')
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(fps)
        
        pygame.quit()

def main():
    """Entry point for the simulation."""
    simulation = Simulation()
    simulation.run()

if __name__ == "__main__":
    main()
