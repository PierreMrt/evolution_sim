"""Main simulation entry point."""

import pygame
import math
from evolution_sim.environment.world import Environment
from evolution_sim.visualization.renderer import Renderer
from evolution_sim.visualization.left_panel import LeftPanel  # NEW
from evolution_sim.visualization.right_panel import RightPanel  # NEW
from evolution_sim.evolution.evolution_tracker import EvolutionTracker
from evolution_sim.config import config

class Simulation:
    """Main simulation controller."""
    
    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer()
        
        # CREATE TRACKER FIRST
        self.tracker = EvolutionTracker()
        
        # Create both panels
        self.left_panel = LeftPanel(self.renderer.screen, self.tracker)
        self.right_panel = RightPanel(self.renderer.screen)
        
        self.environment = Environment()
        
        # Register initial population
        for creature in self.environment.creatures:
            self.tracker.register_birth(creature)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.selected_creature = None
    
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
                    # Check right panel first
                    if self.right_panel.handle_click(event.pos):
                        self.selected_creature = self.right_panel.selected_creature
                    else:
                        # Try to select creature at mouse position
                        self._select_creature_at(event.pos[0], event.pos[1])
    
    def _select_creature_at(self, x: int, y: int) -> None:
        """Select a creature at the given position."""
        # Get world boundaries
        world_rect = self.renderer.get_world_rect()
        
        # Check if click is inside world area
        if not world_rect.collidepoint(x, y):
            return
        
        # Convert screen coordinates to world coordinates
        world_x = x - world_rect.x
        world_y = y - world_rect.y
        
        for creature in self.environment.creatures:
            if creature.alive:
                dist = math.sqrt((creature.x - world_x)**2 + (creature.y - world_y)**2)
                if dist < creature.radius + 5:
                    self.selected_creature = creature
                    self.right_panel.select_creature(creature)
                    return
        
        # If no creature clicked, deselect
        self.selected_creature = None
        self.right_panel.select_creature(None)
    
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
                self.right_panel.select_creature(None)
            
            # Update tracker statistics
            self.tracker.update(self.environment)
    
    def render(self) -> None:
        """Render simulation."""
        # Draw world in center
        self.renderer.draw(self.environment, self.selected_creature)
        
        # Draw left panel
        self.left_panel.draw(self.environment, self.tracker.current_frame)
        
        # Draw right panel
        self.right_panel.draw(self.environment)
        
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
