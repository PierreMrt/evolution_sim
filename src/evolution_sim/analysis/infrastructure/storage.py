"""Orchestrates file storage and directory management."""

import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd
from evolution_sim.analysis.infrastructure.parquet_adapter import ParquetAdapter

logger = logging.getLogger(__name__)


class AnalysisStorage:
    """Manages file paths and coordinates saving analysis data."""
    
    def __init__(self, base_dir: str = "simulation_data"):
        """
        Initialize storage manager.
        
        Args:
            base_dir: Base directory for all simulation runs
        """
        self.base_dir = Path(base_dir)
        self.run_dir: Optional[Path] = None
        self.adapter = ParquetAdapter()
        
    def create_run_directory(self) -> Path:
        """
        Create a new timestamped run directory.
        
        Returns:
            Path to created run directory
            
        Raises:
            IOError: If directory cannot be created
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.run_dir = self.base_dir / f"run_{timestamp}"
            self.run_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created run directory: {self.run_dir}")
            return self.run_dir
        except Exception as e:
            logger.error(f"Failed to create run directory: {e}")
            raise IOError(f"Cannot create run directory: {e}")
    
    def copy_config(self, config_path: str = "config/config.yaml") -> None:
        """
        Copy configuration file to run directory.
        
        Args:
            config_path: Path to source config file
            
        Raises:
            IOError: If config cannot be copied
        """
        try:
            if self.run_dir is None:
                raise RuntimeError("Run directory not created")
            
            source = Path(config_path)
            if not source.exists():
                logger.warning(f"Config file not found: {config_path}")
                return
            
            destination = self.run_dir / "config.yaml"
            shutil.copy2(source, destination)
            logger.info(f"Copied config to {destination}")
        except Exception as e:
            logger.error(f"Failed to copy config: {e}")
            raise IOError(f"Cannot copy config: {e}")
    
    def save_global_metrics(self, df: pd.DataFrame) -> None:
        """
        Save global metrics DataFrame.
        
        Args:
            df: DataFrame containing global metrics
        """
        if self.run_dir is None:
            raise RuntimeError("Run directory not created")
        
        filepath = self.run_dir / "global_metrics.parquet"
        self.adapter.append_to_parquet(df, filepath)
    
    def save_creature_snapshots(self, df: pd.DataFrame) -> None:
        """
        Save creature snapshots DataFrame.
        
        Args:
            df: DataFrame containing creature snapshots
        """
        if self.run_dir is None:
            raise RuntimeError("Run directory not created")
        
        filepath = self.run_dir / "creature_snapshots.parquet"
        self.adapter.append_to_parquet(df, filepath)
    
    def save_plant_positions(self, df: pd.DataFrame) -> None:
        """
        Save plant positions DataFrame.
        
        Args:
            df: DataFrame containing plant positions
        """
        if self.run_dir is None:
            raise RuntimeError("Run directory not created")
        
        filepath = self.run_dir / "plant_positions.parquet"
        self.adapter.append_to_parquet(df, filepath)
    
    def get_run_directory(self) -> Optional[Path]:
        """Get current run directory path."""
        return self.run_dir
