"""
Vital Stats Suite - Core Interfaces and Base Data Structures
Defines standardized data classes, result models, reference populations, and validation helpers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd


# Standard World Population (WHO Standard 2000-2025 by 5-year age groups per 100,000)
WHO_STANDARD_POPULATION_5YR: Dict[str, float] = {
    "0-4": 8860,
    "5-9": 8690,
    "10-14": 8600,
    "15-19": 8470,
    "20-24": 8220,
    "25-29": 7930,
    "30-34": 7610,
    "35-39": 7150,
    "40-44": 6590,
    "45-49": 6040,
    "50-54": 5370,
    "55-59": 4550,
    "60-64": 3720,
    "65-69": 2960,
    "70-74": 2210,
    "75-79": 1520,
    "80-84": 910,
    "85+": 630,
}

# Standard World Population (Segi 1960 Standard Population per 100,000)
SEGI_STANDARD_POPULATION_5YR: Dict[str, float] = {
    "0-4": 12000,
    "5-9": 10000,
    "10-14": 9000,
    "15-19": 9000,
    "20-24": 8000,
    "25-29": 8000,
    "30-34": 6000,
    "35-39": 6000,
    "40-44": 6000,
    "45-49": 6000,
    "50-54": 5000,
    "55-59": 4000,
    "60-64": 4000,
    "65-69": 3000,
    "70-74": 2000,
    "75-79": 1000,
    "80-84": 500,
    "85+": 500,
}


@dataclass
class DemographicMeasureResult:
    """Standard container for the result of any demographic calculation."""
    code: str
    name: str
    block: str  # 'A: Sex Composition', 'B: Age Composition', 'C: Fertility', 'D: Mortality'
    raw_value: float
    formatted_value: str
    unit: str
    formula: str
    citation: str
    interpretation: Optional[Dict[str, Any]] = None
    inputs_used: Dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "block": self.block,
            "raw_value": self.raw_value,
            "formatted_value": self.formatted_value,
            "unit": self.unit,
            "formula": self.formula,
            "citation": self.citation,
            "interpretation": self.interpretation,
            "inputs_used": self.inputs_used,
            "notes": self.notes,
        }


@dataclass
class QualityCheckResult:
    """Standard container for demographic data quality evaluation."""
    check_code: str
    name: str
    score: Optional[float]
    status: str  # 'EXCELLENT', 'ACCEPTABLE', 'WARNING', 'SEVERE', 'MISSING_DATA'
    summary: str
    interpretation: str
    recommendation: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_code": self.check_code,
            "name": self.name,
            "score": self.score,
            "status": self.status,
            "summary": self.summary,
            "interpretation": self.interpretation,
            "recommendation": self.recommendation,
            "details": self.details,
        }


@dataclass
class DemographicDataset:
    """
    Standard tabular container for census, survey, or vital registration data.
    Supports age distributions, sex splits, fertility schedules, and mortality schedules.
    """
    name: str = "Demographic Dataset"
    year: Optional[int] = None
    region: Optional[str] = None
    
    # Population totals
    total_population: Optional[float] = None
    male_population: Optional[float] = None
    female_population: Optional[float] = None
    
    # Age group totals (Broad age groups)
    pop_0_14: Optional[float] = None
    pop_15_64: Optional[float] = None
    pop_65_plus: Optional[float] = None
    
    # Detailed tables
    # Single-year age table: columns ['age', 'male', 'female', 'total']
    single_year_ages: Optional[pd.DataFrame] = None
    
    # 5-year age table: columns ['age_group', 'male', 'female', 'total']
    age_group_5yr: Optional[pd.DataFrame] = None
    
    # Vital events totals
    total_live_births: Optional[float] = None
    male_births: Optional[float] = None
    female_births: Optional[float] = None
    marital_births: Optional[float] = None
    married_women_15_49: Optional[float] = None
    total_women_15_49: Optional[float] = None
    
    # Fertility by maternal 5-year age group (15-19, 20-24, ..., 45-49)
    # columns ['age_group', 'female_pop', 'births', 'female_births' (optional)]
    fertility_schedule: Optional[pd.DataFrame] = None
    
    # Mortality counts
    total_deaths: Optional[float] = None
    male_deaths: Optional[float] = None
    female_deaths: Optional[float] = None
    neonatal_deaths: Optional[float] = None   # < 28 days
    infant_deaths: Optional[float] = None     # < 1 year
    child_deaths_1_4: Optional[float] = None  # age 1-4
    pop_1_4: Optional[float] = None
    
    # Mortality schedule by age group
    # columns ['age_group', 'population', 'deaths']
    mortality_schedule: Optional[pd.DataFrame] = None
    
    # Life table fragment for NRR calculation if available
    # columns ['age_group', 'nLx', 'lx', 'p_survival']
    life_table_female: Optional[pd.DataFrame] = None
    
    # Standard population for age standardization
    # columns ['age_group', 'standard_pop', 'standard_deaths' (optional)]
    standard_population: Optional[pd.DataFrame] = None
    
    # PEC (Post-Enumeration Check) / Coverage factors
    pec_omission_rate: Optional[float] = None  # e.g., 0.035 for 3.5% undercount
    pec_completeness_rate: Optional[float] = None  # e.g., 0.965 for 96.5% completeness
    
    # Metadata & Raw data dictionary
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_df: Optional[pd.DataFrame] = None
