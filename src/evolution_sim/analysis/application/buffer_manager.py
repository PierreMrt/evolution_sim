"""Manages DataFrame buffers for batch writing."""

import logging
from typing import Optional, Tuple
import pandas as pd
from evolution_sim.analysis.domain.metrics import (
    GlobalMetrics,
    CreatureSnapshot,
    PlantPosition
)

logger = logging.getLogger(__name__)


class BufferManager:
    """Manages in-memory buffers for analysis data."""
    
    def __init__(self, buffer_size: int = 300):
        """
        Initialize buffer manager.
        
        Args:
            buffer_size: Number of frames to buffer before flushing
        """
        self.buffer_size = buffer_size
        self.global_buffer: list = []
        self.creature_buffer: list = []
        self.plant_buffer: list = []
        
    def add_global_metrics(self, metrics: GlobalMetrics) -> None:
        """
        Add global metrics to buffer.
        
        Args:
            metrics: GlobalMetrics instance
        """
        self.global_buffer.append(metrics.to_dict())
        
    def add_creature_snapshots(self, snapshots: list[CreatureSnapshot]) -> None:
        """
        Add creature snapshots to buffer.
        
        Args:
            snapshots: List of CreatureSnapshot instances
        """
        for snapshot in snapshots:
            self.creature_buffer.append(snapshot.to_dict())
    
    def add_plant_positions(self, positions: list[PlantPosition]) -> None:
        """
        Add plant positions to buffer.
        
        Args:
            positions: List of PlantPosition instances
        """
        for position in positions:
            self.plant_buffer.append(position.to_dict())
    
    def should_flush(self) -> bool:
        """
        Check if buffers should be flushed.
        
        Returns:
            True if any buffer has reached buffer_size
        """
        return (
            len(self.global_buffer) >= self.buffer_size or
            len(self.creature_buffer) >= self.buffer_size or
            len(self.plant_buffer) >= self.buffer_size
        )
    
    def get_and_clear(
        self
    ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Get DataFrames from buffers and clear them.
        
        Returns:
            Tuple of (global_df, creature_df, plant_df)
            Returns None for empty buffers
        """
        # Create DataFrames
        global_df = pd.DataFrame(self.global_buffer) if self.global_buffer else None
        creature_df = pd.DataFrame(self.creature_buffer) if self.creature_buffer else None
        plant_df = pd.DataFrame(self.plant_buffer) if self.plant_buffer else None
        
        # Clear buffers
        self.global_buffer = []
        self.creature_buffer = []
        self.plant_buffer = []
        
        if global_df is not None:
            logger.debug(f"Flushing {len(global_df)} global metrics")
        if creature_df is not None:
            logger.debug(f"Flushing {len(creature_df)} creature snapshots")
        if plant_df is not None:
            logger.debug(f"Flushing {len(plant_df)} plant positions")
        
        return global_df, creature_df, plant_df
    
    def get_buffer_sizes(self) -> dict:
        """
        Get current buffer sizes.
        
        Returns:
            Dictionary with buffer sizes
        """
        return {
            'global': len(self.global_buffer),
            'creature': len(self.creature_buffer),
            'plant': len(self.plant_buffer)
        }
