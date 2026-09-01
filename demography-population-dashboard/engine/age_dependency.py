"""
Block B: Age Composition & Dependency Measures
Implements:
4. Age Composition Ratio (ACR) - Breakdown across Young (0-14), Working (15-64), Old (65+)
5. Total Dependency Ratio (TDR)
6. Child Dependency Ratio (CDR_child)
7. Old-Age Dependency Ratio (OADR)

References:
- United Nations DESA Population Division (2022). World Population Prospects.
- Rowland, D. T. (2003). Demographic Methods and Concepts. Oxford University Press.
- Bhende, A., & Kanitkar, T. (2010). Principles of Population Studies.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd
from engine.base import DemographicMeasureResult, DemographicDataset


def calculate_age_composition_ratio(
    pop_0_14: float,
    pop_15_64: float,
    pop_65_plus: float,
    total_population: Optional[float] = None,
) -> DemographicMeasureResult:
    """
    Calculate Age Composition Ratio (ACR).
    ACR gives the percentage share of each functional age group:
    - Young Age Share (0-14): (P_0_14 / Total) * 100
    - Working Age Share (15-64): (P_15_64 / Total) * 100
    - Elderly Age Share (65+): (P_65_plus / Total) * 100
    
    Returns structured result with working-age share as primary value and full breakdown in inputs.
    """
    if total_population is None:
        total_population = pop_0_14 + pop_15_64 + pop_65_plus
        
    if total_population <= 0:
        raise ValueError("Total population must be strictly positive.")
        
    pct_0_14 = (pop_0_14 / total_population) * 100.0
    pct_15_64 = (pop_15_64 / total_population) * 100.0
    pct_65_plus = (pop_65_plus / total_population) * 100.0
    
    return DemographicMeasureResult(
        code="ACR",
        name="Age Composition Ratio",
        block="B: Age Composition & Dependency",
        raw_value=pct_15_64,
        formatted_value=f"Working: {pct_15_64:.1f}% | Young: {pct_0_14:.1f}% | Elderly: {pct_65_plus:.1f}%",
        unit="%",
        formula="ACR_i = (Population in Age Bracket i / Total Population) * 100",
        citation="Rowland (2003), Demographic Methods and Concepts, Ch. 3",
        inputs_used={
            "pop_0_14": pop_0_14,
            "pop_15_64": pop_15_64,
            "pop_65_plus": pop_65_plus,
            "total_population": total_population,
            "pct_0_14": pct_0_14,
            "pct_15_64": pct_15_64,
            "pct_65_plus": pct_65_plus,
        },
        notes="A working-age share > 60-65% indicates an expansive demographic dividend window."
    )


def calculate_total_dependency_ratio(
    pop_0_14: float,
    pop_15_64: float,
    pop_65_plus: float,
    per: int = 100,
) -> DemographicMeasureResult:
    """
    Calculate Total Dependency Ratio (TDR).
    TDR = ((Pop 0-14 + Pop 65+) / Pop 15-64) * 100
    
    Formula: TDR = ((P_0_14 + P_65+) / P_15_64) * 100
    """
    if pop_15_64 <= 0:
        raise ValueError("Working-age population (15-64) must be strictly positive.")
        
    tdr_val = ((pop_0_14 + pop_65_plus) / pop_15_64) * float(per)
    
    return DemographicMeasureResult(
        code="TDR",
        name="Total Dependency Ratio",
        block="B: Age Composition & Dependency",
        raw_value=tdr_val,
        formatted_value=f"{tdr_val:.2f} dependents per {per} working-age persons",
        unit=f"per {per} working-age",
        formula=f"TDR = ((P_0_14 + P_65+) / P_15_64) * {per}",
        citation="UN DESA Demographic Indicators; Rowland (2003), Ch. 3",
        inputs_used={
            "pop_0_14": pop_0_14,
            "pop_15_64": pop_15_64,
            "pop_65_plus": pop_65_plus,
            "per": per,
        },
        notes="Global benchmark: < 50 indicates high economic support window; > 70 indicates high dependency burden."
    )


def calculate_child_dependency_ratio(
    pop_0_14: float,
    pop_15_64: float,
    per: int = 100,
) -> DemographicMeasureResult:
    """
    Calculate Child Dependency Ratio (CDR_child / YDR).
    CDR_child = (Pop 0-14 / Pop 15-64) * 100
    
    Formula: CDR_child = (P_0_14 / P_15_64) * 100
    """
    if pop_15_64 <= 0:
        raise ValueError("Working-age population (15-64) must be strictly positive.")
        
    cdr_child_val = (pop_0_14 / pop_15_64) * float(per)
    
    return DemographicMeasureResult(
        code="CDR_CHILD",
        name="Child Dependency Ratio",
        block="B: Age Composition & Dependency",
        raw_value=cdr_child_val,
        formatted_value=f"{cdr_child_val:.2f} children per {per} working-age persons",
        unit=f"per {per} working-age",
        formula=f"CDR_child = (P_0_14 / P_15_64) * {per}",
        citation="Bhende & Kanitkar (2010), Principles of Population Studies, Ch. 5",
        inputs_used={
            "pop_0_14": pop_0_14,
            "pop_15_64": pop_15_64,
            "per": per,
        },
        notes="High child dependency (> 45) reflects youthful fertility requiring educational investment."
    )


def calculate_old_age_dependency_ratio(
    pop_65_plus: float,
    pop_15_64: float,
    per: int = 100,
) -> DemographicMeasureResult:
    """
    Calculate Old-Age Dependency Ratio (OADR / EDR).
    OADR = (Pop 65+ / Pop 15-64) * 100
    
    Formula: OADR = (P_65+ / P_15_64) * 100
    """
    if pop_15_64 <= 0:
        raise ValueError("Working-age population (15-64) must be strictly positive.")
        
    oadr_val = (pop_65_plus / pop_15_64) * float(per)
    
    return DemographicMeasureResult(
        code="OADR",
        name="Old-Age Dependency Ratio",
        block="B: Age Composition & Dependency",
        raw_value=oadr_val,
        formatted_value=f"{oadr_val:.2f} elderly per {per} working-age persons",
        unit=f"per {per} working-age",
        formula=f"OADR = (P_65+ / P_15_64) * {per}",
        citation="UN DESA Population Division; Rowland (2003), Ch. 3",
        inputs_used={
            "pop_65_plus": pop_65_plus,
            "pop_15_64": pop_15_64,
            "per": per,
        },
        notes="Values > 20 indicate rapid population aging, placing pressure on pension and healthcare systems."
    )


def extract_broad_age_groups_from_tables(dataset: DemographicDataset) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Helper to extract or derive (0-14, 15-64, 65+) from 5-year or single-year age tables."""
    p_0_14 = dataset.pop_0_14
    p_15_64 = dataset.pop_15_64
    p_65_plus = dataset.pop_65_plus
    
    if (p_0_14 is not None) and (p_15_64 is not None) and (p_65_plus is not None):
        return p_0_14, p_15_64, p_65_plus
        
    # Check 5-year table
    if dataset.age_group_5yr is not None:
        df = dataset.age_group_5yr.copy()
        tot_col = "total" if "total" in df.columns else ("male" if "male" in df.columns else df.columns[1])
        if "male" in df.columns and "female" in df.columns and "total" not in df.columns:
            df["total"] = df["male"] + df["female"]
            tot_col = "total"
            
        young_groups = ["0-4", "5-9", "10-14"]
        work_groups = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64"]
        old_groups = ["65-69", "70-74", "75-79", "80-84", "85+", "80+"]
        
        y_sum = df[df["age_group"].isin(young_groups)][tot_col].sum()
        w_sum = df[df["age_group"].isin(work_groups)][tot_col].sum()
        o_sum = df[df["age_group"].isin(old_groups)][tot_col].sum()
        
        if y_sum > 0 and w_sum > 0:
            return float(y_sum), float(w_sum), float(o_sum)
            
    # Check single-year table
    if dataset.single_year_ages is not None:
        df = dataset.single_year_ages.copy()
        tot_col = "total" if "total" in df.columns else ("male" if "male" in df.columns else df.columns[1])
        if "male" in df.columns and "female" in df.columns and "total" not in df.columns:
            df["total"] = df["male"] + df["female"]
            tot_col = "total"
            
        y_sum = df[(df["age"] >= 0) & (df["age"] <= 14)][tot_col].sum()
        w_sum = df[(df["age"] >= 15) & (df["age"] <= 64)][tot_col].sum()
        o_sum = df[df["age"] >= 65][tot_col].sum()
        
        if y_sum > 0 and w_sum > 0:
            return float(y_sum), float(w_sum), float(o_sum)
            
    return p_0_14, p_15_64, p_65_plus


def compute_block_b(dataset: DemographicDataset) -> Dict[str, DemographicMeasureResult]:
    """Compute all Block B measures from a demographic dataset."""
    results: Dict[str, DemographicMeasureResult] = {}
    
    p_0_14, p_15_64, p_65_plus = extract_broad_age_groups_from_tables(dataset)
    t_pop = dataset.total_population
    if t_pop is None and p_0_14 is not None and p_15_64 is not None and p_65_plus is not None:
        t_pop = p_0_14 + p_15_64 + p_65_plus
        
    if p_0_14 is not None and p_15_64 is not None and p_65_plus is not None:
        results["ACR"] = calculate_age_composition_ratio(p_0_14, p_15_64, p_65_plus, t_pop)
        results["TDR"] = calculate_total_dependency_ratio(p_0_14, p_15_64, p_65_plus)
        results["CDR_CHILD"] = calculate_child_dependency_ratio(p_0_14, p_15_64)
        results["OADR"] = calculate_old_age_dependency_ratio(p_65_plus, p_15_64)
        
    return results
