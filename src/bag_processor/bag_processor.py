# Copyright 2024
# Author: Usamah Zaheer
from pathlib import Path
import rosbag2_py # Because it uses the efficient SequentialReader and SequentialWriter plus more...
import logging
from src.utils.prepare_directories import prepare_directories
from src.utils.extract_poses import write_pose_message, open_pose_files, close_pose_files

class BagProcessor:
    """
    A class to process ROS2 bag files and extract pose data into segments.
    
    Attributes:
        bag_path (Path): Path to the input ROS2 bag file
        output_dir (Path): Directory where processed segments will be stored
        logger (Logger): Logger for general messages
        perf_logger (Logger): Logger for performance-related messages
        storage_options_base (dict): Base storage options for ROS2 bag
        converter_options (ConverterOptions): Options for ROS2 bag conversion
    """

    def __init__(self, bag_path: str, output_dir: str):
        self.bag_path = Path(bag_path)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        self.perf_logger = logging.getLogger('performance')
        
        self.logger.info(f"Initializing BagProcessor with bag: {bag_path}")
        self.logger.info(f"Output directory set to: {output_dir}")
        
        self.storage_options_base = {
            'storage_id': 'sqlite3'
        }
        self.converter_options = rosbag2_py.ConverterOptions(
            input_serialization_format='cdr',
            output_serialization_format='cdr'
        )

    def process_bag(self, segment_duration: int = 60) -> list:
        """
        Process the ROS2 bag file and split it into time-based segments.
        
        Args:
            segment_duration (int): Duration of each segment in seconds. Defaults to 60.
            
        Returns:
            list: List of Path objects pointing to valid segment directories
            
        Raises:
            Various exceptions related to bag reading/writing operations
        """
        prepare_directories(self.output_dir)  # Initial setup
        
        storage_options = rosbag2_py.StorageOptions(
            uri=str(self.bag_path),
            **self.storage_options_base
        )
        
        reader = rosbag2_py.SequentialReader()
        reader.open(storage_options, self.converter_options)
        
        topic_types = reader.get_all_topics_and_types()
        
        pose_topics = [
            topic.name for topic in topic_types 
            if topic.type == 'geometry_msgs/msg/PoseStamped'
        ]
        
        segment_start_time = None
        segment_paths = []
        current_segment_poses = {}
        current_segment = None
        
        topic_last_timestamp = {topic: None for topic in pose_topics}
        
        while reader.has_next():
            topic_name, data, timestamp = reader.read_next()
            
            current_segment_end = (segment_start_time or 0) + segment_duration * 1e9
            if segment_start_time is None or timestamp >= current_segment_end:
                if current_segment_poses:
                    close_pose_files(current_segment_poses)
                
                segment_start_time = current_segment_end if segment_start_time is not None else timestamp
                segment_path, current_segment = self._create_new_segment(len(segment_paths))
                segment_paths.append(segment_path)
                
                current_segment_poses = open_pose_files(segment_path, pose_topics)
                
                for topic in pose_topics:
                    topic_metadata = rosbag2_py.TopicMetadata(
                        name=topic,
                        type='geometry_msgs/msg/PoseStamped',
                        serialization_format='cdr'
                    )
                    current_segment.create_topic(topic_metadata)
            
            write_pose_message(
                topic_name, data, timestamp,
                current_segment, current_segment_poses
            )
            
            if topic_name in pose_topics:
                topic_last_timestamp[topic_name] = timestamp
        
        if current_segment_poses:
            close_pose_files(current_segment_poses)
        
        valid_segments = []
        for segment_path in segment_paths:
            pose_files = list((segment_path / "poses").glob('*.txt'))
            if len(pose_files) < 2:
                continue
            
            pose_counts = []
            for pose_file in pose_files:
                with open(pose_file, 'r') as f:
                    pose_counts.append(sum(1 for _ in f))
            
            max_diff = max(pose_counts) - min(pose_counts)
            if max_diff > 500:
                self.logger.warning(
                    f"Skipping segment {segment_path.name}: Pose count difference too large "
                    f"(max: {max(pose_counts)}, min: {min(pose_counts)})"
                )
                continue
            
            valid_segments.append(segment_path)
        return valid_segments
    
    def _create_new_segment(self, segment_index: int) -> tuple:
        """
        Create a new bag segment with necessary directory structure.
        
        Args:
            segment_index (int): Index number for the segment
            
        Returns:
            tuple: (Path to segment directory, SequentialWriter instance)
        """
        segment_dir = prepare_directories(self.output_dir, segment_index)
        
        storage_options = rosbag2_py.StorageOptions(
            uri=str(segment_dir / 'bag' / str('segment_' + str(segment_index))),
            **self.storage_options_base
        )
        
        writer = rosbag2_py.SequentialWriter()
        writer.open(storage_options, self.converter_options)
        
        return segment_dir, writer