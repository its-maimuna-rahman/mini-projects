"""
Block A: Sex Composition Measures
Implements:
1. Masculinity Proportion (MP)
2. Sex Ratio (SR)
3. Excess of Males (Absolute & Relative)

References:
- Shryock, H. S., Siegel, J. S., & Associates. (1976). The Methods and Materials of Demography. Academic Press.
- Bhende, A., & Kanitkar, T. (2010). Principles of Population Studies. Himalaya Publishing House.
- United Nations Principles and Recommendations for Population and Housing Censuses.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from engine.base import DemographicMeasureResult, DemographicDataset


def calculate_masculinity_proportion(
    male_population: float,
    female_population: Optional[float] = None,
    total_population: Optional[float] = None,
) -> DemographicMeasureResult:
    """
    Calculate Masculinity Proportion (MP).
    MP = (Male Population / Total Population) * 100
    
    Formula: MP = (P_m / P_t) * 100
    """
    if total_population is None:
        if female_population is None:
            raise ValueError("Either total_population or female_population must be provided.")
        total_population = male_population + female_population
    
    if total_population <= 0:
        raise ValueError("Total population must be strictly positive.")
    if male_population < 0:
        raise ValueError("Male population cannot be negative.")
        
    mp_val = (male_population / total_population) * 100.0
    
    return DemographicMeasureResult(
        code="MP",
        name="Masculinity Proportion",
        block="A: Sex Composition",
        raw_value=mp_val,
        formatted_value=f"{mp_val:.2f}%",
        unit="%",
        formula="MP = (Male Population / Total Population) * 100",
        citation="Shryock & Siegel (1976), The Methods and Materials of Demography, Ch. 7",
        inputs_used={
            "male_population": male_population,
            "female_population": female_population,
            "total_population": total_population,
        },
        notes="Measures the percentage of the total population that is male. Balanced baseline ~49.0% - 51.5%."
    )


def calculate_sex_ratio(
    male_population: float,
    female_population: float,
    per: int = 100,
) -> DemographicMeasureResult:
    """
    Calculate Sex Ratio (SR).
    SR = (Male Population / Female Population) * per
    Standard demographic convention: per = 100 (Males per 100 Females).
    
    Formula: SR = (P_m / P_f) * 100
    """
    if female_population <= 0:
        raise ValueError("Female population must be strictly positive.")
    if male_population < 0:
        raise ValueError("Male population cannot be negative.")
        
    sr_val = (male_population / female_population) * float(per)
    
    return DemographicMeasureResult(
        code="SR",
        name="Sex Ratio",
        block="A: Sex Composition",
        raw_value=sr_val,
        formatted_value=f"{sr_val:.2f} males per {per} females",
        unit=f"males per {per} females",
        formula=f"SR = (Male Population / Female Population) * {per}",
        citation="UN Demographic Yearbook; Shryock & Siegel (1976), Ch. 7",
        inputs_used={
            "male_population": male_population,
            "female_population": female_population,
            "per": per,
        },
        notes="Standard biological sex ratio at birth is ~105 males per 100 females. National SR typically ranges 95-105."
    )


def calculate_excess_of_males(
    male_population: float,
    female_population: float,
    total_population: Optional[float] = None,
) -> DemographicMeasureResult:
    """
    Calculate Excess of Males (Absolute and Percentage).
    Absolute Excess = Male Population - Female Population
    Percentage Excess = ((Male Population - Female Population) / Total Population) * 100
    
    Formula: E_m = P_m - P_f
    """
    if total_population is None:
        total_population = male_population + female_population
        
    if total_population <= 0:
        raise ValueError("Total population must be strictly positive.")
        
    abs_excess = male_population - female_population
    pct_excess = (abs_excess / total_population) * 100.0
    
    sign_str = "+" if abs_excess > 0 else ""
    
    return DemographicMeasureResult(
        code="EXCESS_M",
        name="Excess of Males",
        block="A: Sex Composition",
        raw_value=abs_excess,
        formatted_value=f"{sign_str}{abs_excess:,.0f} ({sign_str}{pct_excess:.2f}%)",
        unit="persons",
        formula="Excess_M = Male Population - Female Population; % Excess = (Excess_M / Total Pop) * 100",
        citation="Bhende & Kanitkar (2010), Principles of Population Studies, Ch. 5",
        inputs_used={
            "male_population": male_population,
            "female_population": female_population,
            "total_population": total_population,
            "percent_excess": pct_excess,
        },
        notes="Positive indicates a male surplus; negative indicates a female surplus."
    )


def compute_block_a(dataset: DemographicDataset) -> Dict[str, DemographicMeasureResult]:
    """Compute all Block A measures from a demographic dataset."""
    results: Dict[str, DemographicMeasureResult] = {}
    
    m_pop = dataset.male_population
    f_pop = dataset.female_population
    t_pop = dataset.total_population
    
    if m_pop is None and dataset.single_year_ages is not None and "male" in dataset.single_year_ages.columns:
        m_pop = float(dataset.single_year_ages["male"].sum())
    if f_pop is None and dataset.single_year_ages is not None and "female" in dataset.single_year_ages.columns:
        f_pop = float(dataset.single_year_ages["female"].sum())
        
    if m_pop is None and dataset.age_group_5yr is not None and "male" in dataset.age_group_5yr.columns:
        m_pop = float(dataset.age_group_5yr["male"].sum())
    if f_pop is None and dataset.age_group_5yr is not None and "female" in dataset.age_group_5yr.columns:
        f_pop = float(dataset.age_group_5yr["female"].sum())
        
    if t_pop is None and m_pop is not None and f_pop is not None:
        t_pop = m_pop + f_pop
        
    if m_pop is not None and t_pop is not None:
        results["MP"] = calculate_masculinity_proportion(m_pop, f_pop, t_pop)
        
    if m_pop is not None and f_pop is not None:
        results["SR"] = calculate_sex_ratio(m_pop, f_pop)
        results["EXCESS_M"] = calculate_excess_of_males(m_pop, f_pop, t_pop)
        
    return results
