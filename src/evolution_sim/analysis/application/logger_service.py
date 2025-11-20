"""Main logging workflow orchestrator."""

import logging
from typing import TYPE_CHECKING
from evolution_sim.analysis.domain.collectors import (
    collect_global_metrics,
    collect_creature_snapshots,
    collect_plant_positions
)
from evolution_sim.analysis.application.buffer_manager import BufferManager
from evolution_sim.analysis.infrastructure.storage import AnalysisStorage

if TYPE_CHECKING:
    from evolution_sim.environment.world import Environment

logger = logging.getLogger(__name__)


class AnalysisLoggerService:
    """Orchestrates the analysis logging workflow."""
    
    def __init__(
        self,
        storage: AnalysisStorage,
        buffer_size: int = 300,
        global_interval: int = 10,
        snapshot_interval: int = 50
    ):
        """
        Initialize logger service.
        
        Args:
            storage: AnalysisStorage instance
            buffer_size: Number of frames to buffer before flushing
            global_interval: Frames between global metrics collection
            snapshot_interval: Frames between snapshot collection
        """
        self.storage = storage
        self.buffer_manager = BufferManager(buffer_size)
        self.global_interval = global_interval
        self.snapshot_interval = snapshot_interval
        
    def log_simulation_frame(self, frame: int, environment: 'Environment') -> None:
        """
        Log a simulation frame.
        
        Args:
            frame: Current frame number
            environment: Environment instance
        """
        try:
            # Collect global metrics every N frames
            if frame % self.global_interval == 0:
                metrics = collect_global_metrics(frame, environment)
                self.buffer_manager.add_global_metrics(metrics)
            
            # Collect snapshots every M frames
            if frame % self.snapshot_interval == 0:
                creature_snapshots = collect_creature_snapshots(frame, environment)
                plant_positions = collect_plant_positions(frame, environment)
                
                self.buffer_manager.add_creature_snapshots(creature_snapshots)
                self.buffer_manager.add_plant_positions(plant_positions)
            
            # Flush if buffer is full
            if self.buffer_manager.should_flush():
                self._flush_buffers()
                
        except Exception as e:
            logger.error(f"Error logging frame {frame}: {e}")
            # Don't raise - keep simulation running
    
    def _flush_buffers(self) -> None:
        """Flush all buffers to disk."""
        try:
            global_df, creature_df, plant_df = self.buffer_manager.get_and_clear()
            
            if global_df is not None and not global_df.empty:
                self.storage.save_global_metrics(global_df)
            
            if creature_df is not None and not creature_df.empty:
                self.storage.save_creature_snapshots(creature_df)
            
            if plant_df is not None and not plant_df.empty:
                self.storage.save_plant_positions(plant_df)
                
            logger.info("Successfully flushed buffers to disk")
        except Exception as e:
            logger.error(f"Error flushing buffers: {e}")
            raise
    
    def finalize(self) -> None:
        """Perform final flush and cleanup."""
        try:
            logger.info("Finalizing analysis logger...")
            self._flush_buffers()
            logger.info("Analysis logging completed successfully")
        except Exception as e:
            logger.error(f"Error during finalization: {e}")
            raise
