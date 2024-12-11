FROM osrf/ros:humble-desktop-full

# Install required packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    ros-humble-rosbag2-py \
    ros-humble-ros2bag \
    ros-humble-rosbag2-storage-default-plugins \
    git \
    ros-humble-rosidl-runtime-py \
    && rm -rf /var/lib/apt/lists/*

# Install evo and compatible numpy version
RUN pip3 install evo numpy==1.24.3 matplotlib==3.7.1

# Create workspace directory
WORKDIR /workspace

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV ROS_DOMAIN_ID=42
ENV PYTHONPATH=/workspace
