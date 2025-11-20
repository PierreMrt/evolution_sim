"""Simple API facade for main.py integration."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from evolution_sim.analysis.infrastructure.storage import AnalysisStorage
from evolution_sim.analysis.application.logger_service import AnalysisLoggerService

if TYPE_CHECKING:
    from evolution_sim.environment.world import Environment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisFacade:
    """
    Simple facade for analysis logging.
    
    Hides internal complexity and provides clean API for main.py.
    """
    
    def __init__(
        self,
        output_base_dir: str = "simulation_data",
        buffer_size: int = 300,
        global_interval: int = 10,
        snapshot_interval: int = 50
    ):
        """
        Initialize analysis facade.
        
        Args:
            output_base_dir: Base directory for simulation data
            buffer_size: Number of frames to buffer before flushing
            global_interval: Frames between global metrics collection
            snapshot_interval: Frames between detailed snapshot collection
        """
        try:
            # Initialize storage
            self.storage = AnalysisStorage(output_base_dir)
            run_dir = self.storage.create_run_directory()
            
            # Copy config file
            self.storage.copy_config()
            
            # Initialize logger service
            self.logger_service = AnalysisLoggerService(
                storage=self.storage,
                buffer_size=buffer_size,
                global_interval=global_interval,
                snapshot_interval=snapshot_interval
            )
            
            logger.info(f"Analysis logging initialized: {run_dir}")
            
        except Exception as e:
            logger.error(f"Failed to initialize analysis facade: {e}")
            raise
    
    def log_frame(self, frame: int, environment: 'Environment') -> None:
        """
        Log a simulation frame.
        
        Args:
            frame: Current frame number
            environment: Environment instance
        """
        try:
            self.logger_service.log_simulation_frame(frame, environment)
        except Exception as e:
            logger.error(f"Error logging frame {frame}: {e}")
            # Don't crash the simulation
    
    def close(self) -> None:
        """Finalize logging and cleanup."""
        try:
            self.logger_service.finalize()
            run_dir = self.storage.get_run_directory()
            logger.info(f"Analysis data saved to: {run_dir}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise
    
    def get_run_directory(self) -> Optional[Path]:
        """
        Get the current run directory path.
        
        Returns:
            Path to run directory or None
        """
        return self.storage.get_run_directory()
