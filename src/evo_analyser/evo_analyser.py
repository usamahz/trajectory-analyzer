# Copyright 2024
# Author: Usamah Zaheer
import evo
from evo.core import metrics, sync
from evo.core.trajectory import PosePath3D
from evo.tools import file_interface
import json
import numpy as np
from pathlib import Path
import logging
import copy
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') 
from evo.tools.settings import SETTINGS
SETTINGS.plot_backend = 'Agg' 
from evo.tools import plot
from src.utils.config import Config

class EvoAnalyser:
    """
    Class for analyzing trajectory data using the EVO toolkit.
    
    Attributes:
        output_dir (Path): Directory for analysis outputs
        logger (Logger): General purpose logger
        perf_logger (Logger): Performance metrics logger
        config (Config): Configuration instance
    """

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        self.perf_logger = logging.getLogger('performance')
        self.config = Config()
        
        self.logger.info(f"Initialising EvoAnalyser with output dir: {output_dir}")
        
    def analyze_segment(self, segment_path: Path) -> dict:
        """
        Analyze a bag segment using EVO tools.
        
        Args:
            segment_path (Path): Path to the bag segment directory
            
        Returns:
            dict: Dictionary containing analysis metrics including ATE, RPE,
                 and trajectory statistics
                 
        Raises:
            ValueError: If no valid pose pairs are found
        """
        # Load trajectories
        traj_est = file_interface.read_tum_trajectory_file(
            str(segment_path / 'poses' / "casestudy_predicted_pose.txt"))
        traj_ref = file_interface.read_tum_trajectory_file(
            str(segment_path / 'poses' / "casestudy_reference_pose.txt"))
   
        # Associate trajectories using evo's sync module
        max_diff = self.config.get('analysis', 'trajectory', 'max_association_diff')
        traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est, max_diff)
        
        # Log trajectory information
        self.logger.info(f"Reference trajectory: {len(traj_ref.positions_xyz)} poses")
        self.logger.info(f"Estimated trajectory: {len(traj_est.positions_xyz)} poses")
        
        if len(traj_ref.positions_xyz) == 0 or len(traj_est.positions_xyz) == 0:
            raise ValueError("No valid pose pairs found after association")

        # Create aligned copy for APE calculation
        traj_est_aligned = copy.deepcopy(traj_est)
        traj_est_aligned.align(traj_ref, 
                              correct_scale=True,  # Enable scale correction
                              correct_only_scale=False,  # Allow rotation and translation too
                              n=-1)
        plots_dir = segment_path / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        
        # Calculate APE metrics using aligned trajectory
        ate = metrics.APE(metrics.PoseRelation.translation_part)
        ate.process_data((traj_ref, traj_est_aligned))

        # Calculate APE rotation metrics
        ate_rot = metrics.APE(metrics.PoseRelation.rotation_angle_deg)
        ate_rot.process_data((traj_ref, traj_est_aligned))
        
        # Calculate RPE metrics
        rpe = metrics.RPE(
            pose_relation=metrics.PoseRelation.translation_part,
            delta=1,  # 1 frame delta
            delta_unit=metrics.Unit.frames,
            all_pairs=False
        )
        rpe.process_data((traj_ref, traj_est))
        
        # Calculate RPE rotation metrics
        rpe_rot = metrics.RPE(
            pose_relation=metrics.PoseRelation.rotation_angle_deg,
            delta=1,
            delta_unit=metrics.Unit.frames,
            all_pairs=False
        )
        rpe_rot.process_data((traj_ref, traj_est))
        metrics_dict = {
            "segment_id": segment_path.name,
            # APE translation metrics
            "ate_rmse": float(ate.get_all_statistics()["rmse"]),
            "ate_mean": float(ate.get_all_statistics()["mean"]),
            "ate_median": float(ate.get_all_statistics()["median"]),
            "ate_std": float(ate.get_all_statistics()["std"]),
            "ate_min": float(ate.get_all_statistics()["min"]),
            "ate_max": float(ate.get_all_statistics()["max"]),
            # APE rotation metrics
            "ate_rot_rmse": float(ate_rot.get_all_statistics()["rmse"]),
            "ate_rot_mean": float(ate_rot.get_all_statistics()["mean"]),
            "ate_rot_median": float(ate_rot.get_all_statistics()["median"]),
            # RPE translation metrics
            "rpe_rmse": float(rpe.get_all_statistics()["rmse"]),
            "rpe_mean": float(rpe.get_all_statistics()["mean"]),
            "rpe_median": float(rpe.get_all_statistics()["median"]),
            # RPE rotation metrics
            "rpe_rot_rmse": float(rpe_rot.get_all_statistics()["rmse"]),
            "rpe_rot_mean": float(rpe_rot.get_all_statistics()["mean"]),
            "rpe_rot_median": float(rpe_rot.get_all_statistics()["median"]),
            # Additional metrics
            "trajectory_length": float(traj_ref.path_length),
            "duration": float(traj_ref.timestamps[-1] - traj_ref.timestamps[0]),
            "average_speed": float(traj_ref.path_length / (traj_ref.timestamps[-1] - traj_ref.timestamps[0])),
            "translation_error_percent": float((ate.get_all_statistics()["mean"] / traj_ref.path_length) * 100),
            # Scale error (if using scale-aware alignment)
            "scale_drift": float(np.linalg.norm(traj_est_aligned.scale_ratio - 1.0)) if hasattr(traj_est_aligned, 'scale_ratio') else 0.0,
            # Success rate
            "tracking_success_rate": float(len(traj_est.positions_xyz) / len(traj_ref.positions_xyz)),
        }
        
        # Save metrics
        metrics_path = segment_path / 'metrics' /f"{segment_path.name}_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics_dict, f, indent=4)
        
        # Generate plots with error colormapping
        self._generate_plots(traj_ref, traj_est, traj_est_aligned, 
                            ate, rpe, segment_path.name, plots_dir)
        
        return metrics_dict
    
    def _generate_plots(self, traj_ref, traj_est, traj_est_aligned, 
                       ate_metric, rpe_metric, segment_name: str, plots_dir: Path):
        """
        Generate and save visualization plots with error colormapping.
        
        Args:
            traj_ref: Reference trajectory
            traj_est: Estimated trajectory
            traj_est_aligned: Aligned estimated trajectory
            ate_metric: Absolute trajectory error metric
            rpe_metric: Relative pose error metric
            segment_name (str): Name of the segment
            plots_dir (Path): Directory to save plots
        """
        plot_collection = evo.tools.plot.PlotCollection("Trajectory Analysis")
        
        # 3D trajectory plots
        fig = plt.figure(figsize=(12, 8))
        plot_mode = plot.PlotMode.xyz
        
        # Original trajectories
        ax = plot.prepare_axis(fig, plot_mode, subplot_arg=221)
        ax.set_title("Original Trajectories")
        plot.traj(ax, plot_mode, traj_ref, '--', 'gray', 'reference')
        plot.traj(ax, plot_mode, traj_est, '-', 'blue', 'estimated')
        
        # Aligned trajectories
        ax = plot.prepare_axis(fig, plot_mode, subplot_arg=222)
        ax.set_title("Aligned Trajectories")
        plot.traj(ax, plot_mode, traj_ref, '--', 'gray', 'reference')
        plot.traj(ax, plot_mode, traj_est_aligned, '-', 'blue', 'estimated (aligned)')
        
        plot_collection.add_figure("Trajectories Comparison", fig)
        
        # Top view with APE colormapping
        fig_top = plt.figure()
        ax = plot.prepare_axis(fig_top, plot.PlotMode.xy)
        plot_collection.add_figure("Top View (APE)", fig_top)
        plot.traj(ax, plot.PlotMode.xy, traj_ref, '--', 'gray', 'reference')
        plot.traj_colormap(ax, traj_est_aligned, ate_metric.error, 
                          plot.PlotMode.xy,
                          min_map=ate_metric.get_all_statistics()["min"],
                          max_map=ate_metric.get_all_statistics()["max"],
                          title="APE Colormapping")
        
        # RPE plot
        fig_rpe = plt.figure()
        ax = fig_rpe.add_subplot(111)
        plot_collection.add_figure("RPE Over Time", fig_rpe)
        seconds_from_start = [t - traj_est.timestamps[0] for t in traj_est.timestamps[1:]]
        plot.error_array(ax, rpe_metric.error, 
                        x_array=seconds_from_start,
                        statistics={s:v for s,v in rpe_metric.get_all_statistics().items() 
                                  if s != "sse"},
                        name="RPE", 
                        title="RPE w.r.t. " + rpe_metric.pose_relation.value,
                        xlabel="t (s)")
        
        # Add RMSE plot
        fig_rmse = plt.figure(figsize=(10, 6))
        ax = fig_rmse.add_subplot(111)
        plot_collection.add_figure("RMSE Analysis", fig_rmse)
        
        # Calculate timestamps in seconds
        timestamps = [t - traj_est.timestamps[0] for t in traj_est.timestamps]
        
        # Plot cumulative RMSE
        cumulative_rmse = np.sqrt(np.cumsum(ate_metric.error ** 2) / 
                                 np.arange(1, len(ate_metric.error) + 1))
        
        ax.plot(timestamps, cumulative_rmse, 
                label=f'Cumulative RMSE (final: {cumulative_rmse[-1]:.3f}m)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('RMSE (m)')
        ax.set_title('Cumulative RMSE Over Time')
        ax.grid(True)
        ax.legend()

        # Add ATE plot
        fig_ate = plt.figure(figsize=(10, 6))
        ax = fig_ate.add_subplot(111)
        plot_collection.add_figure("ATE Analysis", fig_ate)
        
        # Plot ATE over time
        timestamps = [t - traj_est.timestamps[0] for t in traj_est.timestamps]
        ax.plot(timestamps, ate_metric.error, 'b-', label='ATE')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('ATE (m)')
        ax.set_title('Absolute Trajectory Error Over Time')
        
        # Add horizontal line for mean ATE
        mean_ate = ate_metric.get_all_statistics()["mean"]
        ax.axhline(y=mean_ate, color='r', linestyle='--', 
                   label=f'Mean ATE: {mean_ate:.3f}m')
        
        ax.grid(True)
        ax.legend()

        # Save all plots
        plot_collection.export(
            plots_dir / f"{segment_name}_plots",
            confirm_overwrite=True
        )