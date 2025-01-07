# Trajectory Localisation Analysis Tool

A comprehensive tool for analysing localisation performance in ROS2 systems. This tool processes ROS2 bags containing pose data, performs trajectory analysis, and provides detailed metrics and visualisations.

## Features

- **Bag Processing**
  - Automatic segmentation of long trajectories
  - Support for PoseStamped messages
  - Configurable segment duration
  - Robust pose count validation

- **Trajectory Analysis**
  - Absolute Trajectory Error (ATE) calculation
  - Relative Pose Error (RPE) metrics
  - Scale drift detection
  - Rotation error analysis

- **Visualisation**
  - 3D trajectory plots
  - Error heat maps
  - Time-series analysis
  - Comparative visualisations

- **Dashboard (TODO)**
  - Real-time metric monitoring
  - Customisable plots
  - Segment comparison
  - Export capabilities

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.23
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/usamahz/trajectory-analyzer.git #Skip this step if you already have the repository cloned
   cd trajectory-analyzer
   ```

2. Build the Docker containers:
   ```bash
   docker-compose build
   ```

## Usage

1. Input Data:
   - Place your ROS2 bag file in `data/input/` along with metadata file `data/input/metadata.json`

2. Run Analysis:
   ```bash
   ./run_analysis.sh
   ```

3. View Results:
   Analysis outputs can be found in the following directories:
   - `data/output/analysis_summary.json` - Overall analysis metrics
   - `data/output/segment_*/plots/` - Visualisation plots for each segment

```
   Note: Interactive dashboard viewing (via `launch_dashboard.sh`) is placeholder and not implemented yet.
```

## Configuration

The tool can be configured through several YAML files:

- Analysis Configuration (`config/default.yaml`):
  - Segment duration
  - Trajectory association parameters
  - Logging settings

## Output Structure

Analysis results are stored in `data/output/` with the following structure:

- `analysis_summary.json`: Overall metrics
- `segment_X/`: Individual segment analysis
  - `poses/`: Trajectory data
  - `plots/`: Visualisation plots
  - `metrics/`: Detailed metrics

## CI/CD Workflow

The project proposes a comprehensive CI/CD pipeline using modern DevOps tools and practices:

### Tools and Infrastructure

1. **Version Control**
   - GitHub for repository and branch management

2. **CI/CD Orchestration**
   - GitHub Actions for automating workflows, builds, and deployments

3. **Containerization**
   - Docker for creating portable, reproducible runtime environments

4. **Infrastructure Automation**
   - Terraform for automated provisioning of cloud resources (AWS EC2, S3)

5. **Artifact Management**
   - AWS S3 for storing build artifacts, intermediate results, and reports

6. **Testing Frameworks**
   - Pytest for unit tests, integration tests, and SLAM metrics validation 

7. **Data Processing Frameworks**
   - Pandas for preprocessing trajectory data
   - ROS2 libraries for bag file parsing and trajectory evaluation

8. **Monitoring and Reporting**
   - Streamlit / Prometheus + Grafana for real-time pipeline monitoring
   - Slack for CI/CD event notifications (build status, failures, nightly runs)
