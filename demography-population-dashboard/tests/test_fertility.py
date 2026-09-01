"""
Unit tests for Block C: Fertility Measures
Verifies CBR, MBR, GFR, ASFR, TFR, GRR, NRR derivations vs worked problems.
"""

import pytest
import pandas as pd
from engine.fertility import (
    calculate_crude_birth_rate,
    calculate_marital_birth_rate,
    calculate_general_fertility_rate,
    calculate_age_specific_fertility_rates,
    calculate_total_fertility_rate,
    calculate_gross_reproduction_rate,
    calculate_net_reproduction_rate,
    compute_block_c,
)
from engine.base import DemographicDataset


def test_crude_birth_rate():
    # 45,000 births in a population of 2,500,000 -> 18.00 per 1000
    res = calculate_crude_birth_rate(total_live_births=45000, total_population=2500000)
    assert pytest.approx(res.raw_value, 0.001) == 18.00


def test_marital_and_general_fertility_rates():
    # 40,000 marital births among 250,000 married women (15-49) -> 160.0 per 1000
    mbr = calculate_marital_birth_rate(marital_live_births=40000, married_women_15_49=250000)
    assert pytest.approx(mbr.raw_value, 0.001) == 160.0
    
    # 45,000 total births among 600,000 total women (15-49) -> 75.0 per 1000
    gfr = calculate_general_fertility_rate(total_live_births=45000, total_women_15_49=600000)
    assert pytest.approx(gfr.raw_value, 0.001) == 75.0


def test_asfr_and_tfr_derivation():
    """
    Standard textbook worked example:
    Age Groups (15-19 .. 45-49), width n = 5
    ASFRs per 1000: [20.0, 110.0, 150.0, 90.0, 40.0, 10.0, 2.0]
    Sum of ASFRs = 422.0
    TFR = 5 * (422.0 / 1000) = 2.110 children per woman.
    """
    asfr_list = [20.0, 110.0, 150.0, 90.0, 40.0, 10.0, 2.0]
    tfr_res = calculate_total_fertility_rate(asfr_list, age_interval=5)
    assert pytest.approx(tfr_res.raw_value, 0.001) == 2.110


def test_grr_and_nrr_derivation():
    """
    Given TFR = 2.110, female birth proportion = 0.4878 (100 / 205):
    GRR = 2.110 * 0.4878 = 1.029 daughters per woman.
    With female survival to childbearing = 0.970:
    NRR = 1.029 * 0.970 = 0.998.
    """
    grr_res = calculate_gross_reproduction_rate(tfr=2.110, female_birth_proportion=100.0/205.0)
    assert pytest.approx(grr_res.raw_value, 0.001) == 1.02927
    
    nrr_res = calculate_net_reproduction_rate(grr=grr_res.raw_value, female_survival_to_childbearing=0.970)
    assert pytest.approx(nrr_res.raw_value, 0.001) == 0.99839


def test_nrr_precise_life_table_integration():
    """
    Verify NRR computation with empirical life table fragment nLx values.
    """
    fert_df = pd.DataFrame({
        "age_group": ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"],
        "female_pop": [10000, 10000, 10000, 10000, 10000, 10000, 10000],
        "births": [200, 1100, 1500, 900, 400, 100, 20],
        "female_births": [98, 537, 732, 439, 195, 49, 10]
    })
    # Life table nLx with radix l0 = 100,000 (n=5 -> max nLx = 500,000)
    life_df = pd.DataFrame({
        "age_group": ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"],
        "nLx": [485000, 482000, 479000, 475000, 470000, 463000, 452000]
    })
    
    nrr_res = calculate_net_reproduction_rate(
        fertility_schedule=fert_df,
        life_table_female=life_df,
        age_interval=5,
        radix=100000.0
    )
    assert nrr_res.raw_value > 0.95
    assert nrr_res.raw_value < 1.05
    assert nrr_res.inputs_used["method"] == "life_table_survival_integration"
