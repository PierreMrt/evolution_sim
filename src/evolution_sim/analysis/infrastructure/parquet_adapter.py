"""Low-level Parquet file operations."""

import logging
from pathlib import Path
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


class ParquetAdapter:
    """Handles low-level Parquet file operations."""
    
    @staticmethod
    def write_parquet(
        df: pd.DataFrame,
        filepath: Path,
        compression: str = 'snappy'
    ) -> None:
        """
        Write DataFrame to Parquet file.
        
        Args:
            df: DataFrame to write
            filepath: Path to output file
            compression: Compression algorithm ('snappy', 'gzip', 'brotli')
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(
                filepath,
                engine='pyarrow',
                compression=compression,
                index=False
            )
            logger.info(f"Wrote {len(df)} rows to {filepath}")
        except Exception as e:
            logger.error(f"Failed to write Parquet file {filepath}: {e}")
            raise IOError(f"Cannot write to {filepath}: {e}")
    
    @staticmethod
    def read_parquet(filepath: Path) -> pd.DataFrame:
        """
        Read DataFrame from Parquet file.
        
        Args:
            filepath: Path to Parquet file
            
        Returns:
            DataFrame loaded from file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        try:
            if not filepath.exists():
                raise FileNotFoundError(f"Parquet file not found: {filepath}")
            
            df = pd.read_parquet(filepath, engine='pyarrow')
            logger.info(f"Read {len(df)} rows from {filepath}")
            return df
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to read Parquet file {filepath}: {e}")
            raise IOError(f"Cannot read from {filepath}: {e}")
    
    @staticmethod
    def append_to_parquet(
        df: pd.DataFrame,
        filepath: Path,
        compression: str = 'snappy'
    ) -> None:
        """
        Append DataFrame to existing Parquet file.
        
        If file doesn't exist, creates a new one.
        
        Args:
            df: DataFrame to append
            filepath: Path to Parquet file
            compression: Compression algorithm
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            if filepath.exists():
                existing_df = ParquetAdapter.read_parquet(filepath)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                ParquetAdapter.write_parquet(combined_df, filepath, compression)
            else:
                ParquetAdapter.write_parquet(df, filepath, compression)
        except Exception as e:
            logger.error(f"Failed to append to Parquet file {filepath}: {e}")
            raise IOError(f"Cannot append to {filepath}: {e}")
