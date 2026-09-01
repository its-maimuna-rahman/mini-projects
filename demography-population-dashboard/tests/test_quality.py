"""
Unit tests for Data Quality Module:
Verifies Whipple's Index, Myers' Blended Index, PEC Coverage, and Schema validation.
"""

import pytest
import pandas as pd
import numpy as np
from engine.quality import (
    calculate_whipples_index,
    calculate_myers_blended_index,
    calculate_pec_comparison,
    validate_dataset_completeness,
    run_all_quality_checks,
)
from engine.base import DemographicDataset


def test_whipples_index_uniform_population():
    """Under a perfectly uniform population distribution across ages 23-62, Whipple's Index must equal 100.0."""
    ages = list(range(23, 63))
    df_uniform = pd.DataFrame({
        "age": ages,
        "total": [1000] * len(ages)
    })
    res = calculate_whipples_index(df_uniform)
    assert pytest.approx(res.score, 0.001) == 100.0
    assert res.status == "EXCELLENT"


def test_whipples_index_heaped_population():
    """Under severe digit heaping (multiplying ages ending in 0 and 5 by 3x), Whipple's Index must be flagged as SEVERE."""
    ages = list(range(23, 63))
    counts = [3000 if a % 5 == 0 else 500 for a in ages]
    df_heaped = pd.DataFrame({"age": ages, "total": counts})
    res = calculate_whipples_index(df_heaped)
    assert res.score > 175.0
    assert res.status == "SEVERE"


def test_myers_blended_index_clean_vs_heaped():
    """Myers index should be low (< 5) on smooth data and elevated on digit-spiked data."""
    ages = list(range(10, 70))
    # Smooth data
    df_clean = pd.DataFrame({
        "age": ages,
        "total": [int(5000 * np.exp(-0.01 * (a - 10))) for a in ages]
    })
    res_clean = calculate_myers_blended_index(df_clean)
    assert res_clean.score < 5.0
    assert res_clean.status == "EXCELLENT"
    
    # Heaped data
    df_heaped = pd.DataFrame({
        "age": ages,
        "total": [15000 if (a % 10 == 0) else 2000 for a in ages]
    })
    res_heaped = calculate_myers_blended_index(df_heaped)
    assert res_heaped.score > 20.0
    assert res_heaped.status == "SEVERE"


def test_pec_dual_system_estimation():
    """
    Census count = 9,500,000
    PEC sample estimate indicates true population = 10,000,000 (Omission rate = 5.0%, Completeness = 95.0%).
    Adjustment factor k = 1 / 0.95 = 1.0526.
    """
    res = calculate_pec_comparison(census_count=9500000, omission_rate=0.05)
    assert pytest.approx(res.score, 0.01) == 5.00
    assert pytest.approx(res.details["completeness_rate"], 0.01) == 0.95
    assert pytest.approx(res.details["adjustment_factor_k"], 0.001) == 1.0526


def test_missing_column_detector():
    """
    Feed an incomplete dataset and assert that missing measures are correctly identified.
    """
    incomplete_ds = DemographicDataset(
        name="Sparse Dataset",
        male_population=50000,
        female_population=50000,
        total_live_births=2000,
        # Missing: age schedules, married women, deaths
    )
    computable, missing, gaps = validate_dataset_completeness(incomplete_ds)
    assert "MP" in computable
    assert "SR" in computable
    assert "CBR" in computable
    assert "TFR" in missing
    assert "CDR" in missing
    assert "ASDR" in missing
    assert len(computable) < 10
