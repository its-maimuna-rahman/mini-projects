"""
Unit tests for Block B: Age Composition & Dependency Measures
Verifies ACR, TDR, Child Dependency Ratio, Old-Age Dependency Ratio.
"""

import pytest
import pandas as pd
from engine.age_dependency import (
    calculate_age_composition_ratio,
    calculate_total_dependency_ratio,
    calculate_child_dependency_ratio,
    calculate_old_age_dependency_ratio,
    compute_block_b,
)
from engine.base import DemographicDataset


def test_dependency_ratios_textbook_example():
    """
    Standard demographic problem:
    Population 0-14 = 300,000
    Population 15-64 = 600,000
    Population 65+ = 100,000
    Total Population = 1,000,000

    Expected:
    - ACR: Working = 60.0%, Young = 30.0%, Old = 10.0%
    - TDR: ((300,000 + 100,000) / 600,000) * 100 = 66.667
    - CDR_child: (300,000 / 600,000) * 100 = 50.0
    - OADR: (100,000 / 600,000) * 100 = 16.667
    """
    p0_14 = 300000.0
    p15_64 = 600000.0
    p65 = 100000.0
    
    acr = calculate_age_composition_ratio(p0_14, p15_64, p65)
    assert pytest.approx(acr.inputs_used["pct_15_64"], 0.01) == 60.0
    assert pytest.approx(acr.inputs_used["pct_0_14"], 0.01) == 30.0
    assert pytest.approx(acr.inputs_used["pct_65_plus"], 0.01) == 10.0
    
    tdr = calculate_total_dependency_ratio(p0_14, p15_64, p65)
    assert pytest.approx(tdr.raw_value, 0.001) == 66.667
    
    cdr = calculate_child_dependency_ratio(p0_14, p15_64)
    assert pytest.approx(cdr.raw_value, 0.001) == 50.0
    
    oadr = calculate_old_age_dependency_ratio(p65, p15_64)
    assert pytest.approx(oadr.raw_value, 0.001) == 16.667


def test_dependency_ratio_sum_identity():
    """Mathematical property: TDR = CDR_child + OADR."""
    p0_14 = 245000.0
    p15_64 = 710000.0
    p65 = 125000.0
    
    tdr = calculate_total_dependency_ratio(p0_14, p15_64, p65).raw_value
    cdr = calculate_child_dependency_ratio(p0_14, p15_64).raw_value
    oadr = calculate_old_age_dependency_ratio(p65, p15_64).raw_value
    
    assert pytest.approx(tdr, 0.0001) == (cdr + oadr)


def test_block_b_from_5yr_table():
    """Verifies that compute_block_b correctly aggregates from 5-year table if totals are not given directly."""
    df_5yr = pd.DataFrame({
        "age_group": ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85+"],
        "total": [1000, 1000, 1000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 500, 500, 500, 300, 200]
    })
    # 0-14 sum = 3000
    # 15-64 sum = 20000
    # 65+ sum = 2000
    ds = DemographicDataset(age_group_5yr=df_5yr)
    res = compute_block_b(ds)
    assert "ACR" in res
    assert "TDR" in res
    assert pytest.approx(res["TDR"].raw_value, 0.01) == 25.0 # (5000 / 20000) * 100 = 25.0
