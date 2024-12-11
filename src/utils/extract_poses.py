# Copyright 2024
# Author: Usamah Zaheer
from rclpy.serialization import deserialize_message
from geometry_msgs.msg import PoseStamped
from pathlib import Path
import logging

def write_pose_message(topic_name, data, timestamp, segment, pose_files):
    """
    Write pose messages to both bag and text files in TUM format.
    
    Args:
        topic_name (str): Name of the ROS topic
        data (bytes): Serialized pose message data
        timestamp (int): Message timestamp in nanoseconds
        segment (SequentialWriter): Bag segment writer
        pose_files (dict): Dictionary of open file handles for pose data
        
    Raises:
        Exception: If writing to bag or text file fails
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Write to bag
        segment.write(topic_name, data, timestamp)
        
        # Write to pose file if applicable
        if topic_name in pose_files:
            msg = deserialize_message(data, PoseStamped)
            pos = msg.pose.position
            ori = msg.pose.orientation
            timestamp_seconds = timestamp / 1e9
            
            # TUM format
            pose_files[topic_name].write(
                f'{timestamp_seconds:.4f} {pos.x:.4f} {pos.y:.4f} {pos.z:.4f} '
                f'{ori.x:.4f} {ori.y:.4f} {ori.z:.4f} {ori.w:.4f}\n'
            )
    except Exception as e:
        logger.error(f"Error writing pose message for topic {topic_name}: {str(e)}")
        raise

def open_pose_files(segment_path: Path, pose_topics: list) -> dict:
    """
    Open text files for writing pose data for each topic.
    
    Args:
        segment_path (Path): Path to the segment directory
        pose_topics (list): List of pose topic names
        
    Returns:
        dict: Dictionary mapping topic names to open file handles
    """
    pose_files = {}
    for topic in pose_topics:
        filename = topic.strip('/').replace('/', '_') + '.txt'
        filepath = segment_path / "poses" / filename
        pose_files[topic] = open(filepath, 'w')
    return pose_files

def close_pose_files(pose_files: dict):
    """
    Close all open pose files.
    
    Args:
        pose_files (dict): Dictionary of open file handles to close
    """
    for fh in pose_files.values():
        fh.close()
