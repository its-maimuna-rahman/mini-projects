"""
Unit tests for End-to-End Pipeline & Two-Dataset Comparison Mode
"""

import json
from pathlib import Path
import pytest
import pandas as pd
from engine.base import DemographicDataset
from engine.pipeline import run_demographic_pipeline, compare_two_datasets

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def load_sample_dataset(file_path: str) -> DemographicDataset:
    with open(file_path, "r") as f:
        data = json.load(f)
        
    ds = DemographicDataset(
        name=data.get("name", "Census"),
        year=data.get("year"),
        region=data.get("region"),
        total_population=data.get("total_population"),
        male_population=data.get("male_population"),
        female_population=data.get("female_population"),
        pop_0_14=data.get("pop_0_14"),
        pop_15_64=data.get("pop_15_64"),
        pop_65_plus=data.get("pop_65_plus"),
        total_live_births=data.get("total_live_births"),
        male_births=data.get("male_births"),
        female_births=data.get("female_births"),
        marital_births=data.get("marital_births"),
        married_women_15_49=data.get("married_women_15_49"),
        total_women_15_49=data.get("total_women_15_49"),
        total_deaths=data.get("total_deaths"),
        neonatal_deaths=data.get("neonatal_deaths"),
        infant_deaths=data.get("infant_deaths"),
        child_deaths_1_4=data.get("child_deaths_1_4"),
        pop_1_4=data.get("pop_1_4"),
        pec_omission_rate=data.get("pec_omission_rate"),
        pec_completeness_rate=data.get("pec_completeness_rate"),
        single_year_ages=pd.DataFrame(data["single_year_ages"]) if "single_year_ages" in data else None,
        fertility_schedule=pd.DataFrame(data["fertility_schedule"]) if "fertility_schedule" in data else None,
        mortality_schedule=pd.DataFrame(data["mortality_schedule"]) if "mortality_schedule" in data else None,
    )
    return ds


def test_end_to_end_pipeline_census_2011():
    ds_2011 = load_sample_dataset(SAMPLE_DATA_DIR / "census_2011.json")
    result = run_demographic_pipeline(ds_2011)
    
    # All 22+ measures should be successfully computed
    assert result.computable_count >= 22
    assert "MP" in result.measures
    assert "TFR" in result.measures
    assert "DSDR" in result.measures
    assert "SMR" in result.measures
    assert "ISDR" in result.measures
    
    # Check TFR is near expected ~2.12
    tfr = result.get_measure("TFR")
    assert tfr is not None
    assert pytest.approx(tfr.raw_value, 0.05) == 2.125
    assert tfr.interpretation is not None
    assert tfr.interpretation["status"] == "EXCELLENT"
    
    # Check data quality checks ran
    assert "WHIPPLE" in result.quality_checks
    assert "MYERS" in result.quality_checks
    assert "PEC" in result.quality_checks
    assert result.quality_checks["WHIPPLE"].status in ("EXCELLENT", "ACCEPTABLE")


def test_two_dataset_comparison():
    ds_2011 = load_sample_dataset(SAMPLE_DATA_DIR / "census_2011.json")
    ds_2022 = load_sample_dataset(SAMPLE_DATA_DIR / "census_2022.json")
    
    comp_result = compare_two_datasets(ds_2011, ds_2022)
    assert comp_result.dataset_a_name == "National Population Census 2011"
    assert comp_result.dataset_b_name == "National Population Census 2022"
    assert len(comp_result.comparison_table) >= 22
    assert len(comp_result.key_divergences) > 0
    
    # Fertility should show a decline from 2011 to 2022
    tfr_divergence = next((d for d in comp_result.key_divergences if d["code"] == "TFR"), None)
    assert tfr_divergence is not None
    assert tfr_divergence["delta"] < 0  # Declined

