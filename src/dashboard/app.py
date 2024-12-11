import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
import logging
from src.utils.logging_config import setup_logging

logger = setup_logging(log_dir="dashboard_logs")
logger.info("Starting analysis dashboard")

def load_metrics(output_dir: str):
    metrics_file = Path(output_dir) / "analysis_summary.json"
    with open(metrics_file) as f:
        return json.load(f)

def main():
    st.title("Localisation Analysis Dashboard")
    
    # Load metrics
    metrics_data = load_metrics("data/output")
    df = pd.DataFrame(metrics_data)
    
    # Overall statistics
    st.header("Overall Performance Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg ATE RMSE", f"{df['ate_rmse'].mean():.3f}")
    with col2:
        st.metric("Avg RPE RMSE", f"{df['rpe_rmse'].mean():.3f}")
    with col3:
        st.metric("Avg Rotation Error", f"{df['ate_rot_rmse'].mean():.3f}°")
    
    # Detailed plots
    st.header("Detailed Analysis")
    
    # ATE over segments
    fig_ate = px.line(df, x='segment_id', y=['ate_rmse', 'ate_mean', 'ate_median'],
                      title="Absolute Trajectory Error Over Segments")
    st.plotly_chart(fig_ate)
    
    # RPE analysis
    fig_rpe = px.line(df, x='segment_id', y=['rpe_rmse', 'rpe_mean', 'rpe_median'],
                      title="Relative Pose Error Over Segments")
    st.plotly_chart(fig_rpe)
    
    # Rotation error analysis
    fig_rot = px.line(df, x='segment_id', y=['ate_rot_rmse', 'ate_rot_mean'],
                      title="Rotation Error Over Segments")
    st.plotly_chart(fig_rot)

if __name__ == "__main__":
    main() 