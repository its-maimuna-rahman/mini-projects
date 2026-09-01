"""
Block D: Mortality & Age Standardization Measures
Implements:
15. Crude Death Rate (CDR)
16. Corrected CDR (under-reporting & PEC adjustment)
17. Neonatal Mortality Rate (NMR)
18. Infant Mortality Rate (IMR)
19. Child Mortality Rate (CMR / U5MR)
20. Age-Specific Death Rate (ASDR)
21. Direct Standardized Rate (DSDR)
22. Standardized Mortality Ratio (SMR) & Indirect Standardized Rate

References:
- Preston, S. H., Heuveline, P., & Guillot, M. (2001). Demography: Measuring and Modeling Population Processes.
- World Health Organization (WHO) Statistical Standards & Global Health Estimates.
- Shryock & Siegel (1976), The Methods and Materials of Demography, Ch. 14 & 15.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
from engine.base import (
    DemographicMeasureResult,
    DemographicDataset,
    WHO_STANDARD_POPULATION_5YR,
)


def calculate_crude_death_rate(
    total_deaths: float,
    total_population: float,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Crude Death Rate (CDR).
    CDR = (Total Deaths / Total Mid-Year Population) * 1000
    
    Formula: CDR = (D / P) * 1000
    """
    if total_population <= 0:
        raise ValueError("Total population must be strictly positive.")
    if total_deaths < 0:
        raise ValueError("Total deaths cannot be negative.")
        
    cdr_val = (total_deaths / total_population) * float(per)
    
    return DemographicMeasureResult(
        code="CDR",
        name="Crude Death Rate",
        block="D: Mortality & Standardization",
        raw_value=cdr_val,
        formatted_value=f"{cdr_val:.2f} deaths per {per:,} population",
        unit=f"deaths per {per:,}",
        formula=f"CDR = (Total Deaths / Total Mid-Year Population) * {per}",
        citation="Preston et al. (2001), Demography: Measuring and Modeling Population Processes, Ch. 2",
        inputs_used={
            "total_deaths": total_deaths,
            "total_population": total_population,
            "per": per,
        },
        notes="Subject to strong age-distribution effects: an older population may have a higher CDR despite better health."
    )


def calculate_corrected_cdr(
    crude_death_rate: Optional[float] = None,
    total_deaths: Optional[float] = None,
    total_population: Optional[float] = None,
    completeness_rate: Optional[float] = None,
    omission_rate: Optional[float] = None,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Corrected Crude Death Rate (adjusted for registration completeness/omission).
    Corrected CDR = CDR / Completeness = CDR / (1 - Omission Rate)
    
    Formula: Corrected CDR = (D / (C * P)) * 1000
    """
    if crude_death_rate is None:
        if total_deaths is None or total_population is None:
            raise ValueError("Must provide either crude_death_rate or both total_deaths and total_population.")
        crude_death_rate = (total_deaths / total_population) * float(per)
        
    if completeness_rate is None:
        if omission_rate is not None:
            if omission_rate >= 1.0 or omission_rate < 0:
                raise ValueError("Omission rate must be between 0.0 and 1.0 (exclusive of 1.0).")
            completeness_rate = 1.0 - omission_rate
        else:
            completeness_rate = 0.95  # Default 95% completeness assumption if unstated
            
    if completeness_rate <= 0 or completeness_rate > 1.0:
        raise ValueError("Completeness rate must be in the range (0.0, 1.0].")
        
    corrected_cdr_val = crude_death_rate / completeness_rate
    
    return DemographicMeasureResult(
        code="CORRECTED_CDR",
        name="Corrected Crude Death Rate",
        block="D: Mortality & Standardization",
        raw_value=corrected_cdr_val,
        formatted_value=f"{corrected_cdr_val:.2f} deaths per {per:,} (adj. at {completeness_rate*100:.1f}% completeness)",
        unit=f"adjusted deaths per {per:,}",
        formula=f"Corrected CDR = CDR / Completeness_Rate = CDR / (1 - Omission_Rate)",
        citation="UN Principles and Recommendations for Vital Statistics; Bennett-Horiuchi (1981)",
        inputs_used={
            "crude_death_rate": crude_death_rate,
            "completeness_rate": completeness_rate,
            "omission_rate": 1.0 - completeness_rate,
            "per": per,
        },
        notes=f"Corrects for an estimated {(1.0 - completeness_rate)*100:.1f}% under-registration in vital recording."
    )


def calculate_neonatal_mortality_rate(
    neonatal_deaths: float,
    total_live_births: float,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Neonatal Mortality Rate (NMR).
    Deaths within the first 28 days of life per 1,000 live births.
    
    Formula: NMR = (D_<28 days / Live Births) * 1000
    """
    if total_live_births <= 0:
        raise ValueError("Total live births must be strictly positive.")
    if neonatal_deaths < 0:
        raise ValueError("Neonatal deaths cannot be negative.")
        
    nmr_val = (neonatal_deaths / total_live_births) * float(per)
    
    return DemographicMeasureResult(
        code="NMR",
        name="Neonatal Mortality Rate",
        block="D: Mortality & Standardization",
        raw_value=nmr_val,
        formatted_value=f"{nmr_val:.2f} deaths per {per:,} live births",
        unit=f"deaths per {per:,} live births",
        formula=f"NMR = (Deaths < 28 days / Live Births) * {per}",
        citation="WHO Global Health Observatory; SDG Target 3.2 (Aim: <= 12 per 1,000)",
        inputs_used={
            "neonatal_deaths": neonatal_deaths,
            "total_live_births": total_live_births,
            "per": per,
        },
        notes="Reflects quality of antenatal, intrapartum, and immediate newborn care."
    )


def calculate_infant_mortality_rate(
    infant_deaths: float,
    total_live_births: float,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Infant Mortality Rate (IMR).
    Deaths before reaching age 1 per 1,000 live births.
    
    Formula: IMR = (D_<1 year / Live Births) * 1000
    """
    if total_live_births <= 0:
        raise ValueError("Total live births must be strictly positive.")
    if infant_deaths < 0:
        raise ValueError("Infant deaths cannot be negative.")
        
    imr_val = (infant_deaths / total_live_births) * float(per)
    
    return DemographicMeasureResult(
        code="IMR",
        name="Infant Mortality Rate",
        block="D: Mortality & Standardization",
        raw_value=imr_val,
        formatted_value=f"{imr_val:.2f} deaths per {per:,} live births",
        unit=f"deaths per {per:,} live births",
        formula=f"IMR = (Deaths < 1 year / Live Births) * {per}",
        citation="UNICEF / WHO Child Mortality Guidelines; Preston et al. (2001), Ch. 2",
        inputs_used={
            "infant_deaths": infant_deaths,
            "total_live_births": total_live_births,
            "per": per,
        },
        notes="Primary bellwether indicator of national public health, nutrition, and environmental sanitation."
    )


def calculate_child_mortality_rate(
    child_deaths_1_4: Optional[float] = None,
    pop_1_4: Optional[float] = None,
    under_5_deaths: Optional[float] = None,
    total_live_births: Optional[float] = None,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Child Mortality Rate (CMR).
    Can be calculated as:
    1. Child Death Rate (ages 1-4): (Deaths 1-4 / Population 1-4) * 1000
    2. Under-5 Mortality Rate (U5MR): (Deaths < 5 / Live Births) * 1000
    """
    if child_deaths_1_4 is not None and pop_1_4 is not None and pop_1_4 > 0:
        cmr_val = (child_deaths_1_4 / pop_1_4) * float(per)
        name = "Child Death Rate (Age 1-4)"
        formula = f"CMR(1-4) = (Deaths 1-4 / Pop 1-4) * {per}"
        unit = f"deaths per {per:,} children (1-4)"
    elif under_5_deaths is not None and total_live_births is not None and total_live_births > 0:
        cmr_val = (under_5_deaths / total_live_births) * float(per)
        name = "Under-5 Mortality Rate (U5MR)"
        formula = f"U5MR = (Deaths < 5 years / Live Births) * {per}"
        unit = f"deaths per {per:,} live births"
    else:
        raise ValueError("Must provide either (child_deaths_1_4 and pop_1_4) or (under_5_deaths and total_live_births).")
        
    return DemographicMeasureResult(
        code="CMR",
        name=name,
        block="D: Mortality & Standardization",
        raw_value=cmr_val,
        formatted_value=f"{cmr_val:.2f} {unit}",
        unit=unit,
        formula=formula,
        citation="UN IGME Child Mortality Estimation; SDG Indicator 3.2.1",
        inputs_used={
            "child_deaths_1_4": child_deaths_1_4,
            "pop_1_4": pop_1_4,
            "under_5_deaths": under_5_deaths,
            "total_live_births": total_live_births,
            "per": per,
        },
        notes="Reflects infectious disease prevalence, malnutrition, and childhood immunization coverage."
    )


def calculate_age_specific_death_rates(
    mortality_schedule: pd.DataFrame,
    per: int = 1000,
) -> Tuple[DemographicMeasureResult, pd.DataFrame]:
    """
    Calculate Age-Specific Death Rates (ASDR).
    mortality_schedule must contain:
    - 'age_group' (e.g. '0-4', '5-9', ..., '85+')
    - 'population' (mid-year population)
    - 'deaths' (number of deaths in that age bracket)
    
    Formula: ASDR_i = (Deaths_i / Population_i) * 1000
    """
    df = mortality_schedule.copy()
    if "population" not in df.columns or "deaths" not in df.columns:
        raise ValueError("mortality_schedule must contain 'population' and 'deaths' columns.")
        
    df["asdr"] = (df["deaths"] / df["population"]) * float(per)
    asdr_dict = dict(zip(df["age_group"], df["asdr"]))
    
    min_row = df.loc[df["asdr"].idxmin()] if not df.empty else None
    min_age = min_row["age_group"] if min_row is not None else "N/A"
    min_val = min_row["asdr"] if min_row is not None else 0.0
    
    return DemographicMeasureResult(
        code="ASDR",
        name="Age-Specific Death Rate Schedule",
        block="D: Mortality & Standardization",
        raw_value=float(df["asdr"].mean()),
        formatted_value=f"U-shaped curve (Min: {min_val:.2f} per {per:,} at Age {min_age})",
        unit=f"deaths per {per:,} population in age group",
        formula=f"ASDR_i = (Deaths_i / Population_i) * {per}",
        citation="Preston et al. (2001), Ch. 2; Shryock & Siegel (1976)",
        inputs_used={
            "asdr_schedule": asdr_dict,
            "lowest_mortality_age_group": min_age,
            "mean_asdr": float(df["asdr"].mean()),
        },
        notes="Standard human mortality curve is U-shaped or bathtub-shaped (elevated in infancy, nadir at 10-14, exponential rise thereafter)."
    ), df


def calculate_direct_standardized_rate(
    mortality_schedule: pd.DataFrame,
    standard_population: Optional[pd.DataFrame] = None,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Direct Standardized Death Rate (DSDR).
    Applies the study population's age-specific death rates to a standard age distribution.
    
    Formula: DSDR = sum( ASDR_i * P_std_i ) / sum( P_std_i )
    """
    df = mortality_schedule.copy()
    if "asdr" not in df.columns:
        if "deaths" in df.columns and "population" in df.columns:
            df["asdr"] = (df["deaths"] / df["population"]) * float(per)
        else:
            raise ValueError("mortality_schedule must contain 'asdr' or ('deaths' and 'population').")
            
    if standard_population is not None:
        std_df = standard_population.copy()
        merged = pd.merge(df, std_df, on="age_group", how="inner")
        std_pop_col = "standard_pop" if "standard_pop" in merged.columns else ("population_std" if "population_std" in merged.columns else merged.columns[-1])
        expected_deaths = (merged["asdr"] * merged[std_pop_col]).sum() / float(per)
        total_std_pop = merged[std_pop_col].sum()
        dsdr_val = (expected_deaths / total_std_pop) * float(per)
        std_name = "User Standard Population"
    else:
        # Use WHO Standard 2000-2025
        who_map = WHO_STANDARD_POPULATION_5YR
        df["std_pop"] = df["age_group"].map(who_map).fillna(0.0)
        
        # If age groups don't match exactly, fallback to broad standard weights
        if df["std_pop"].sum() == 0:
            df["std_pop"] = 1.0 / len(df)
            
        expected_deaths = (df["asdr"] * df["std_pop"]).sum() / float(per)
        total_std_pop = df["std_pop"].sum()
        dsdr_val = (expected_deaths / total_std_pop) * float(per)
        std_name = "WHO World Standard Population (2000-2025)"
        
    return DemographicMeasureResult(
        code="DSDR",
        name="Direct Standardized Death Rate",
        block="D: Mortality & Standardization",
        raw_value=dsdr_val,
        formatted_value=f"{dsdr_val:.2f} standardized deaths per {per:,} ({std_name})",
        unit=f"standardized deaths per {per:,}",
        formula="DSDR = sum( ASDR_i * P_std_i ) / sum( P_std_i )",
        citation="WHO Guidelines for Standardized Rates; Preston et al. (2001), Ch. 2",
        inputs_used={
            "standard_population_type": std_name,
            "total_standard_population": float(total_std_pop),
            "expected_standard_deaths": float(expected_deaths),
        },
        notes="Direct standardization removes age-structure confounding, enabling direct cross-country and temporal comparisons."
    )


def calculate_smr_and_indirect_standardized_rate(
    observed_deaths: float,
    mortality_schedule: pd.DataFrame,
    standard_population: Optional[pd.DataFrame] = None,
    standard_crude_death_rate: Optional[float] = None,
    per: int = 1000,
) -> Tuple[DemographicMeasureResult, DemographicMeasureResult]:
    """
    Calculate Standardized Mortality Ratio (SMR) and Indirect Standardized Death Rate (ISDR).
    
    Formula:
    Expected Deaths (E) = sum( P_i * ASDR_std_i ) / 1000
    SMR = Observed Deaths / Expected Deaths
    ISDR = SMR * Standard CDR
    """
    df = mortality_schedule.copy()
    if "population" not in df.columns:
        raise ValueError("mortality_schedule must contain 'population' column.")
        
    if standard_population is not None and "asdr_std" in standard_population.columns:
        merged = pd.merge(df, standard_population, on="age_group", how="inner")
        expected_deaths = (merged["population"] * merged["asdr_std"] / float(per)).sum()
        if standard_crude_death_rate is None and "deaths_std" in standard_population.columns and "population_std" in standard_population.columns:
            standard_crude_death_rate = (standard_population["deaths_std"].sum() / standard_population["population_std"].sum()) * float(per)
    elif standard_population is not None and "deaths_std" in standard_population.columns and "population_std" in standard_population.columns:
        merged = pd.merge(df, standard_population, on="age_group", how="inner")
        asdr_std = (merged["deaths_std"] / merged["population_std"]) * float(per)
        expected_deaths = (merged["population"] * asdr_std / float(per)).sum()
        if standard_crude_death_rate is None:
            standard_crude_death_rate = (standard_population["deaths_std"].sum() / standard_population["population_std"].sum()) * float(per)
    else:
        # Derive standard rates from a typical baseline or self-contained reference
        if "asdr" in df.columns:
            # Toy / baseline standard as 1.0 multiplier
            expected_deaths = (df["population"] * df["asdr"] / float(per)).sum()
            standard_crude_death_rate = (observed_deaths / df["population"].sum()) * float(per)
        else:
            expected_deaths = observed_deaths
            standard_crude_death_rate = (observed_deaths / df["population"].sum()) * float(per) if df["population"].sum() > 0 else 8.0
            
    if expected_deaths <= 0:
        raise ValueError("Expected deaths calculation resulted in non-positive value.")
        
    smr_val = observed_deaths / expected_deaths
    if standard_crude_death_rate is None:
        standard_crude_death_rate = 8.0  # WHO baseline CDR approximation
        
    isdr_val = smr_val * standard_crude_death_rate
    
    smr_res = DemographicMeasureResult(
        code="SMR",
        name="Standardized Mortality Ratio",
        block="D: Mortality & Standardization",
        raw_value=smr_val,
        formatted_value=f"{smr_val:.3f} (or {smr_val*100:.1f}%) [Obs: {observed_deaths:,.0f} / Exp: {expected_deaths:,.1f}]",
        unit="ratio (Obs / Exp)",
        formula="SMR = Observed Deaths / Expected Deaths = D / sum( P_i * ASDR_std_i )",
        citation="Breslow & Day (1987); Preston et al. (2001), Ch. 2",
        inputs_used={
            "observed_deaths": observed_deaths,
            "expected_deaths": expected_deaths,
            "smr_percentage": smr_val * 100.0,
        },
        notes="SMR > 1.0 (or > 100%) indicates excess mortality relative to standard population age-specific risk."
    )
    
    isdr_res = DemographicMeasureResult(
        code="ISDR",
        name="Indirect Standardized Death Rate",
        block="D: Mortality & Standardization",
        raw_value=isdr_val,
        formatted_value=f"{isdr_val:.2f} deaths per {per:,} (Indirectly standardized)",
        unit=f"indirectly standardized deaths per {per:,}",
        formula="ISDR = SMR * Standard CDR",
        citation="Shryock & Siegel (1976), Ch. 14; Preston et al. (2001)",
        inputs_used={
            "smr": smr_val,
            "standard_cdr": standard_crude_death_rate,
            "per": per,
        },
        notes="Indirect standardization is ideal when age-specific death counts in the study population are small or unavailable."
    )
    
    return smr_res, isdr_res


def compute_block_d(dataset: DemographicDataset) -> Dict[str, DemographicMeasureResult]:
    """Compute all Block D mortality & standardization measures from a demographic dataset."""
    results: Dict[str, DemographicMeasureResult] = {}
    
    d_tot = dataset.total_deaths
    t_pop = dataset.total_population
    b_tot = dataset.total_live_births
    
    if d_tot is None and dataset.mortality_schedule is not None and "deaths" in dataset.mortality_schedule.columns:
        d_tot = float(dataset.mortality_schedule["deaths"].sum())
        
    # 15. CDR
    cdr_val = None
    if d_tot is not None and t_pop is not None:
        cdr_res = calculate_crude_death_rate(d_tot, t_pop)
        results["CDR"] = cdr_res
        cdr_val = cdr_res.raw_value
        
    # 16. Corrected CDR
    if cdr_val is not None:
        comp_rate = dataset.pec_completeness_rate
        if comp_rate is None and dataset.pec_omission_rate is not None:
            comp_rate = 1.0 - dataset.pec_omission_rate
        results["CORRECTED_CDR"] = calculate_corrected_cdr(
            crude_death_rate=cdr_val,
            completeness_rate=comp_rate,
            omission_rate=dataset.pec_omission_rate
        )
        
    # 17. NMR
    if dataset.neonatal_deaths is not None and b_tot is not None:
        results["NMR"] = calculate_neonatal_mortality_rate(dataset.neonatal_deaths, b_tot)
        
    # 18. IMR
    if dataset.infant_deaths is not None and b_tot is not None:
        results["IMR"] = calculate_infant_mortality_rate(dataset.infant_deaths, b_tot)
        
    # 19. CMR
    if (dataset.child_deaths_1_4 is not None and dataset.pop_1_4 is not None) or (dataset.infant_deaths is not None and b_tot is not None):
        if dataset.child_deaths_1_4 is not None and dataset.pop_1_4 is not None:
            results["CMR"] = calculate_child_mortality_rate(
                child_deaths_1_4=dataset.child_deaths_1_4,
                pop_1_4=dataset.pop_1_4
            )
        elif dataset.infant_deaths is not None and dataset.child_deaths_1_4 is not None and b_tot is not None:
            u5_deaths = dataset.infant_deaths + dataset.child_deaths_1_4
            results["CMR"] = calculate_child_mortality_rate(
                under_5_deaths=u5_deaths,
                total_live_births=b_tot
            )
            
    # 20. ASDR, 21. DSDR, 22. SMR + ISDR
    if dataset.mortality_schedule is not None:
        asdr_res, mort_df = calculate_age_specific_death_rates(dataset.mortality_schedule)
        results["ASDR"] = asdr_res
        
        # Direct Standardization
        dsdr_res = calculate_direct_standardized_rate(mort_df, dataset.standard_population)
        results["DSDR"] = dsdr_res
        
        # Indirect Standardization & SMR
        if d_tot is not None:
            smr_res, isdr_res = calculate_smr_and_indirect_standardized_rate(
                observed_deaths=d_tot,
                mortality_schedule=mort_df,
                standard_population=dataset.standard_population
            )
            results["SMR"] = smr_res
            results["ISDR"] = isdr_res
            
    return results
