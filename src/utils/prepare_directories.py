# Copyright 2024
# Author: Usamah Zaheer
from pathlib import Path
import shutil
import logging
import time

def prepare_directories(output_dir: str, segment_index: int = None) -> Path:
    """
    Prepare directories for bag processing or segment creation.
    
    Args:
        output_dir (str): The base output directory
        segment_index (int, optional): If provided, creates segment-specific directories
            
    Returns:
        Path: Path to created directory
        
    Note:
        If segment_index is None, handles main output directory setup
        If segment_index is provided, creates segment subdirectories
    """
    logger = logging.getLogger(__name__)
    
    logger.info(f"Preparing directories for output_dir: {output_dir}")
    if segment_index is not None:
        logger.info(f"Creating segment directory for index: {segment_index}")
    
    output_path = Path(output_dir)
    if segment_index is None:
        # Handle main output directory setup
        if output_path.exists():
            logger = logging.getLogger(__name__)
            logger.info(f"Cleaning up existing output directory: {output_path}")
            shutil.rmtree(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
        
    # Create segment directory with proper numbering
    segment_dir = output_path / f"segment_{segment_index}"
    
    # Create directory structure and subdirectories
    for subdir in ['poses', 'plots', 'metrics']:
        (segment_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    return segment_dir 