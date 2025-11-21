"""Main simulation entry point."""

import pygame
import math
import logging
from evolution_sim.environment.world import Environment
from evolution_sim.visualization.renderer import Renderer
from evolution_sim.visualization.left_panel import LeftPanel
from evolution_sim.visualization.right_panel import RightPanel
from evolution_sim.evolution.evolution_tracker import EvolutionTracker
from evolution_sim.analysis import AnalysisFacade  # NEW IMPORT
from evolution_sim.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def warmup_numba(environment):
    """
    Pre-compiles Numba neural logic before main simulation loop.
    """
    if environment.creatures:
        brain = environment.creatures[0].brain
        n_inputs = brain._n_inputs if hasattr(brain, "_n_inputs") else 8  # Fallback if unknown
        dummy_inputs = [0.0] * n_inputs
        brain.forward(dummy_inputs)
        logger.info("Numba compilation complete")


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
        
        # Warmup Numba compilation before simulation starts
        warmup_numba(self.environment)
        
        # Initialize analysis logger (NEW)
        try:
            self.analysis_logger = AnalysisFacade(
                output_base_dir="simulation_data",
                buffer_size=300,
                global_interval=10,
                snapshot_interval=50
            )
            logger.info("Analysis logging enabled")
        except Exception as e:
            logger.warning(f"Analysis logging disabled: {e}")
            self.analysis_logger = None
        
        # Register initial population
        for creature in self.environment.creatures:
            self.tracker.register_birth(creature)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.selected_creature = None
        self.current_frame = 0  # NEW: Track frame number
    
    def handle_events(self) -> None:
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:  # NEW: ESC to quit
                    self.running = False
            
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
            
            # Log analysis data (NEW)
            if self.analysis_logger:
                self.analysis_logger.log_frame(self.current_frame, self.environment)
            
            self.current_frame += 1
    
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
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(fps)
        finally:
            # Cleanup (NEW)
            if self.analysis_logger:
                logger.info("Closing analysis logger...")
                self.analysis_logger.close()
            
            pygame.quit()


def main():
    """Entry point for the simulation."""
    simulation = Simulation()
    simulation.run()


if __name__ == "__main__":
    main()
