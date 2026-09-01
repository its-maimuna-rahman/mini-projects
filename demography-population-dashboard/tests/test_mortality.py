"""
Unit tests for Block D: Mortality & Age Standardization Measures
Verifies CDR, Corrected CDR, NMR, IMR, CMR, ASDR, Direct DSDR, SMR & Indirect ISDR reconciliation.
"""

import pytest
import pandas as pd
import numpy as np
from engine.mortality import (
    calculate_crude_death_rate,
    calculate_corrected_cdr,
    calculate_neonatal_mortality_rate,
    calculate_infant_mortality_rate,
    calculate_child_mortality_rate,
    calculate_age_specific_death_rates,
    calculate_direct_standardized_rate,
    calculate_smr_and_indirect_standardized_rate,
    compute_block_d,
)
from engine.base import DemographicDataset


def test_crude_and_corrected_cdr():
    # 20,000 deaths in 2,500,000 population -> 8.00 per 1000
    cdr = calculate_crude_death_rate(total_deaths=20000, total_population=2500000)
    assert pytest.approx(cdr.raw_value, 0.001) == 8.00
    
    # Corrected CDR with 96% completeness (4% undercount) -> 8.00 / 0.96 = 8.333
    corr_cdr = calculate_corrected_cdr(crude_death_rate=8.0, completeness_rate=0.96)
    assert pytest.approx(corr_cdr.raw_value, 0.001) == 8.3333


def test_neonatal_and_infant_mortality():
    # 400 neonatal deaths & 800 infant deaths in 50,000 live births
    # NMR = (400 / 50,000) * 1000 = 8.00 per 1000
    # IMR = (800 / 50,000) * 1000 = 16.00 per 1000
    nmr = calculate_neonatal_mortality_rate(neonatal_deaths=400, total_live_births=50000)
    imr = calculate_infant_mortality_rate(infant_deaths=800, total_live_births=50000)
    
    assert pytest.approx(nmr.raw_value, 0.001) == 8.00
    assert pytest.approx(imr.raw_value, 0.001) == 16.00


def test_child_mortality():
    # Child death rate: 150 deaths in 75,000 children aged 1-4 -> 2.00 per 1000
    cmr = calculate_child_mortality_rate(child_deaths_1_4=150, pop_1_4=75000)
    assert pytest.approx(cmr.raw_value, 0.001) == 2.00


def test_direct_and_indirect_standardization_reconciliation():
    """
    Acceptance Criteria Requirement:
    Direct and Indirect standardized rates must reconcile on a known standard test population.
    When the study population has the exact same age-specific death rates as the standard population,
    SMR must equal 1.000, and DSDR == ISDR == Standard CDR.
    """
    age_groups = ["0-14", "15-64", "65+"]
    std_pop = [300000, 600000, 100000]
    std_deaths = [600, 2400, 5000]  # Total = 8,000 deaths / 1,000,000 pop -> Standard CDR = 8.0 per 1000
    std_asdr = [2.0, 4.0, 50.0]     # Deaths per 1000
    
    # Study population with different age distribution (Younger population: 40% young, 50% work, 10% old)
    study_pop = [400000, 500000, 100000]
    # But EXACT same ASDRs as standard (2.0, 4.0, 50.0)
    study_deaths = [800, 2000, 5000] # Total = 7,800 deaths / 1,000,000 pop -> Study CDR = 7.8 per 1000
    
    mort_df = pd.DataFrame({
        "age_group": age_groups,
        "population": study_pop,
        "deaths": study_deaths,
    })
    
    std_df = pd.DataFrame({
        "age_group": age_groups,
        "standard_pop": std_pop,
        "deaths_std": std_deaths,
        "asdr_std": std_asdr,
        "population_std": std_pop,
    })
    
    # 1. Direct Standardization
    dsdr_res = calculate_direct_standardized_rate(mortality_schedule=mort_df, standard_population=std_df)
    # Expected DSDR = sum(study_asdr * std_pop) / sum(std_pop) = (2.0*300k + 4.0*600k + 50.0*100k) / 1000k = (600 + 2400 + 5000) / 1000 = 8.00 per 1000
    assert pytest.approx(dsdr_res.raw_value, 0.001) == 8.00
    
    # 2. Indirect Standardization & SMR
    smr_res, isdr_res = calculate_smr_and_indirect_standardized_rate(
        observed_deaths=sum(study_deaths),
        mortality_schedule=mort_df,
        standard_population=std_df,
        standard_crude_death_rate=8.0
    )
    # Expected deaths in study pop = (400k*2.0 + 500k*4.0 + 100k*50.0) / 1000 = 800 + 2000 + 5000 = 7,800
    # Observed deaths = 7,800 -> SMR = 7,800 / 7,800 = 1.000
    assert pytest.approx(smr_res.raw_value, 0.001) == 1.000
    # ISDR = SMR * Standard CDR = 1.000 * 8.00 = 8.00 per 1000
    assert pytest.approx(isdr_res.raw_value, 0.001) == 8.00
    
    # Reconciles exactly!
    assert pytest.approx(dsdr_res.raw_value, 0.001) == isdr_res.raw_value
