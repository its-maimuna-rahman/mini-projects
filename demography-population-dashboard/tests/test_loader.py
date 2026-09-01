"""
Unit tests for Universal CSV/JSON Demographic Loader & Comparison
"""

import io
import pytest
import pandas as pd
from engine.loader import (
    load_demographic_dataset,
    generate_sample_age_distribution_csv,
    generate_sample_summary_csv,
)
from engine.pipeline import run_demographic_pipeline, compare_two_datasets


def test_load_sample_age_distribution_csv():
    csv_text = generate_sample_age_distribution_csv()
    ds = load_demographic_dataset(csv_text, name="Test Age Distribution")
    
    assert ds.name == "Test Age Distribution"
    assert ds.total_population is not None and ds.total_population > 0
    assert ds.male_population is not None and ds.male_population > 0
    assert ds.female_population is not None and ds.female_population > 0
    assert ds.pop_0_14 is not None and ds.pop_0_14 > 0
    assert ds.pop_15_64 is not None and ds.pop_15_64 > 0
    assert ds.pop_65_plus is not None and ds.pop_65_plus > 0
    assert ds.age_group_5yr is not None and len(ds.age_group_5yr) == 18
    assert ds.fertility_schedule is not None and len(ds.fertility_schedule) == 7
    assert ds.mortality_schedule is not None and len(ds.mortality_schedule) == 18

    # Pipeline calculation
    result = run_demographic_pipeline(ds)
    assert result.computable_count >= 20
    assert result.get_measure("TFR") is not None
    assert result.get_measure("CDR") is not None
    assert result.get_measure("SR") is not None


def test_load_sample_summary_csv():
    csv_text = generate_sample_summary_csv()
    ds = load_demographic_dataset(csv_text, name="Test Indicators")
    
    assert ds.total_population == 11765000
    assert ds.male_population == 5920000
    assert ds.female_population == 5845000
    assert ds.total_live_births == 225400
    assert ds.total_deaths == 100860

    result = run_demographic_pipeline(ds)
    assert result.get_measure("CBR") is not None
    assert result.get_measure("CDR") is not None
    assert result.get_measure("IMR") is not None


def test_compare_two_csv_datasets():
    csv1 = generate_sample_age_distribution_csv()
    # Modify second CSV to have distinct vital events
    csv2 = """indicator,value
name,Dataset B (Indicators)
year,2022
total_population,8500000
male_population,4200000
female_population,4300000
pop_0_14,1800000
pop_15_64,5900000
pop_65_plus,800000
total_live_births,110000
total_deaths,75000
"""
    ds1 = load_demographic_dataset(csv1, name="Dataset A (Age Table)")
    ds2 = load_demographic_dataset(csv2, name="Dataset B (Indicators)")
    
    comp_res = compare_two_datasets(ds1, ds2)
    assert comp_res.dataset_a_name == "Dataset A (Age Table)"
    assert comp_res.dataset_b_name == "Dataset B (Indicators)"
    assert len(comp_res.comparison_table) >= 20
    assert len(comp_res.key_divergences) > 0
