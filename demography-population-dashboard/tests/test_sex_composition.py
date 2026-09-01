"""
Unit tests for Block A: Sex Composition Measures
Verifies MP, SR, Excess of Males against textbook worked examples (e.g. Bhende & Kanitkar).
"""

import pytest
from engine.sex_composition import (
    calculate_masculinity_proportion,
    calculate_sex_ratio,
    calculate_excess_of_males,
    compute_block_a,
)
from engine.base import DemographicDataset


def test_masculinity_proportion_textbook_example():
    """
    Textbook Problem: A population has 51,200 males and 48,800 females (Total = 100,000).
    Expected MP = (51,200 / 100,000) * 100 = 51.20%.
    """
    res = calculate_masculinity_proportion(male_population=51200, female_population=48800)
    assert pytest.approx(res.raw_value, 0.001) == 51.20
    assert res.code == "MP"
    assert "%" in res.formatted_value


def test_sex_ratio_textbook_example():
    """
    Textbook Problem: In a district, Male Pop = 525,000, Female Pop = 500,000.
    Expected SR = (525,000 / 500,000) * 100 = 105.00 males per 100 females.
    """
    res = calculate_sex_ratio(male_population=525000, female_population=500000, per=100)
    assert pytest.approx(res.raw_value, 0.001) == 105.00
    assert res.code == "SR"
    assert "105.00" in res.formatted_value


def test_excess_of_males():
    """
    Textbook Problem: Males = 600,000, Females = 550,000, Total = 1,150,000.
    Absolute excess = +50,000.
    Percentage excess = (50,000 / 1,150,000) * 100 = 4.3478%.
    """
    res = calculate_excess_of_males(male_population=600000, female_population=550000)
    assert res.raw_value == 50000
    assert pytest.approx(res.inputs_used["percent_excess"], 0.001) == 4.3478


def test_block_a_dataset_computation():
    ds = DemographicDataset(
        name="Test District",
        male_population=102000,
        female_population=98000,
        total_population=200000,
    )
    results = compute_block_a(ds)
    assert "MP" in results
    assert "SR" in results
    assert "EXCESS_M" in results
    assert pytest.approx(results["MP"].raw_value, 0.01) == 51.0
    assert pytest.approx(results["SR"].raw_value, 0.01) == 104.08


def test_sex_composition_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_sex_ratio(male_population=100, female_population=0)
    with pytest.raises(ValueError):
        calculate_masculinity_proportion(male_population=-5, total_population=100)
