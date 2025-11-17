"""Main simulation entry point."""

import pygame
from evolution_sim.environment.world import Environment
from evolution_sim.visualization.renderer import Renderer
from evolution_sim.visualization.stats_display import StatsDisplay
from evolution_sim.config import config


class Simulation:
    """Main simulation controller."""
    
    def __init__(self):
        """Initialize the simulation."""
        self.renderer = Renderer()
        self.stats_display = StatsDisplay(self.renderer.screen)
        self.environment = Environment()
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.paused = False
        
    def handle_events(self) -> None:
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
    
    def update(self) -> None:
        """Update simulation state."""
        if not self.paused:
            self.environment.update()
    
    def render(self) -> None:
        """Render simulation."""
        self.renderer.draw(self.environment)
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
