"""
Unit tests for Module 2: Inference & Policy Engine
"""

from pathlib import Path
import pytest
import pandas as pd
from engine.inference import simulate_demographic_trajectory


def test_trajectory_simulation_projections():
    data_path = Path(__file__).resolve().parent.parent / "sample_data" / "time_series_1970_2024.csv"
    ts_df = pd.read_csv(data_path)
    res = simulate_demographic_trajectory(
        historical_df=ts_df,
        projection_horizon_years=30,
        fertility_scenario="medium",
    )
    
    assert len(res.projected_df) == 30
    assert len(res.combined_df) == len(ts_df) + 30
    assert res.current_phase != ""
    assert len(res.assumptions_summary) > 0
    assert len(res.policy_flags) > 0
    
    # Check that older dependency rises in projected years
    last_hist_oadr = ts_df.iloc[-1]["oadr"]
    final_proj_oadr = res.projected_df.iloc[-1]["oadr"]
    assert final_proj_oadr > last_hist_oadr
