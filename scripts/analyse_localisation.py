import os
import yaml
import json
from pathlib import Path
from src.bag_processor.bag_processor import BagProcessor
from src.evo_analyser.evo_analyser import EvoAnalyser
from src.utils.logging_config import setup_logging

def main():
    """
    Main entry point for the localisation analysis pipeline.
    
    Workflow:
    1. Sets up logging
    2. Loads configuration and paths
    3. Processes ROS2 bag file into segments
    4. Analyzes each segment using EVO toolkit
    5. Saves analysis results and generates visualizations
    
    Note:
        Expects input data in data/input directory
        Outputs results to data/output directory
    """
    # Setup logging
    logger = setup_logging()
    logger.info("Starting localisation analysis pipeline")
    
    # Load paths and config
    script_dir = Path(__file__).parent.parent
    bag_path = script_dir / "data" / "input" / "casestudy_data_0.db3"
    config_path = script_dir / "data" / "input" / "metadata.yaml"
    output_dir = script_dir / "data" / "output"
    
    logger.info(f"Using bag file: {bag_path}")
    logger.info(f"Using config file: {config_path}")
    
    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process bag file and extracting poses
    logger.info("Processing bag file and extracting poses...")
    processor = BagProcessor(bag_path, output_dir)
    segment_paths = processor.process_bag(
        segment_duration=config.get("segment_duration", 60)
    )
    
    # Analyze segments
    logger.info("Analyzing segments...")
    analyzer = EvoAnalyser(output_dir)
    all_metrics = []
    
    for segment_path in segment_paths:
        logger.info(f"Analyzing segment: {segment_path.name}")
        metrics = analyzer.analyze_segment(segment_path)
        all_metrics.append(metrics)
        
    # Save overall results
    results_path = os.path.join(output_dir, "analysis_summary.json")
    with open(results_path, 'w') as f:
        json.dump(all_metrics, f, indent=4)
        
    logger.info(f"Analysis complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main()