"""
Block C: Fertility Measures
Implements:
8. Crude Birth Rate (CBR)
9. Marital Birth Rate (MBR / General Marital Fertility Rate)
10. General Fertility Rate (GFR)
11. Age-Specific Fertility Rate (ASFR)
12. Total Fertility Rate (TFR)
13. Gross Reproduction Rate (GRR)
14. Net Reproduction Rate (NRR)

References:
- Preston, S. H., Heuveline, P., & Guillot, M. (2001). Demography: Measuring and Modeling Population Processes. Blackwell.
- Newell, C. (1988). Methods and Models in Demography. Guilford Press.
- Bhende, A., & Kanitkar, T. (2010). Principles of Population Studies.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd
from engine.base import DemographicMeasureResult, DemographicDataset


def calculate_crude_birth_rate(
    total_live_births: float,
    total_population: float,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Crude Birth Rate (CBR).
    CBR = (Total Live Births / Total Mid-Year Population) * 1000
    
    Formula: CBR = (B / P) * 1000
    """
    if total_population <= 0:
        raise ValueError("Total population must be strictly positive.")
    if total_live_births < 0:
        raise ValueError("Live births cannot be negative.")
        
    cbr_val = (total_live_births / total_population) * float(per)
    
    return DemographicMeasureResult(
        code="CBR",
        name="Crude Birth Rate",
        block="C: Fertility",
        raw_value=cbr_val,
        formatted_value=f"{cbr_val:.2f} births per {per:,} population",
        unit=f"births per {per:,}",
        formula=f"CBR = (Total Live Births / Total Mid-Year Population) * {per}",
        citation="Preston et al. (2001), Demography: Measuring and Modeling Population Processes, Ch. 5",
        inputs_used={
            "total_live_births": total_live_births,
            "total_population": total_population,
            "per": per,
        },
        notes="Global benchmark: < 15 is low (developed), 15-30 is moderate, > 30 is high fertility."
    )


def calculate_marital_birth_rate(
    marital_live_births: float,
    married_women_15_49: float,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate Marital Birth Rate (MBR / General Marital Fertility Rate - GMFR).
    MBR = (Live Births to Married Women / Married Women Aged 15-49) * 1000
    
    Formula: MBR = (B_m / W_m(15-49)) * 1000
    """
    if married_women_15_49 <= 0:
        raise ValueError("Married women (15-49) must be strictly positive.")
    if marital_live_births < 0:
        raise ValueError("Marital live births cannot be negative.")
        
    mbr_val = (marital_live_births / married_women_15_49) * float(per)
    
    return DemographicMeasureResult(
        code="MBR",
        name="Marital Birth Rate (GMFR)",
        block="C: Fertility",
        raw_value=mbr_val,
        formatted_value=f"{mbr_val:.2f} births per {per:,} married women (15-49)",
        unit=f"births per {per:,} married women",
        formula=f"MBR = (Marital Live Births / Married Women 15-49) * {per}",
        citation="Newell (1988), Methods and Models in Demography, Ch. 4; Bhende & Kanitkar (2010)",
        inputs_used={
            "marital_live_births": marital_live_births,
            "married_women_15_49": married_women_15_49,
            "per": per,
        },
        notes="Measures legitimate fertility pressure within marriage independently of marital status distribution."
    )


def calculate_general_fertility_rate(
    total_live_births: float,
    total_women_15_49: float,
    per: int = 1000,
) -> DemographicMeasureResult:
    """
    Calculate General Fertility Rate (GFR).
    GFR = (Total Live Births / Total Women of Reproductive Age 15-49) * 1000
    
    Formula: GFR = (B / W(15-49)) * 1000
    """
    if total_women_15_49 <= 0:
        raise ValueError("Women of reproductive age (15-49) must be strictly positive.")
    if total_live_births < 0:
        raise ValueError("Live births cannot be negative.")
        
    gfr_val = (total_live_births / total_women_15_49) * float(per)
    
    return DemographicMeasureResult(
        code="GFR",
        name="General Fertility Rate",
        block="C: Fertility",
        raw_value=gfr_val,
        formatted_value=f"{gfr_val:.2f} births per {per:,} women (15-49)",
        unit=f"births per {per:,} women (15-49)",
        formula=f"GFR = (Total Live Births / Total Women 15-49) * {per}",
        citation="Shryock & Siegel (1976), Ch. 16; Preston et al. (2001)",
        inputs_used={
            "total_live_births": total_live_births,
            "total_women_15_49": total_women_15_49,
            "per": per,
        },
        notes="Refines CBR by restricting the denominator strictly to women exposed to childbearing."
    )


def calculate_age_specific_fertility_rates(
    fertility_schedule: pd.DataFrame,
    per: int = 1000,
) -> Tuple[DemographicMeasureResult, pd.DataFrame]:
    """
    Calculate Age-Specific Fertility Rates (ASFR).
    fertility_schedule must contain:
    - 'age_group' (e.g. '15-19', '20-24', ..., '45-49')
    - 'female_pop' (number of women in age bracket)
    - 'births' (number of live births to women in age bracket)
    
    Formula: ASFR_i = (Births_i / Women_i) * 1000
    """
    df = fertility_schedule.copy()
    if "female_pop" not in df.columns or "births" not in df.columns:
        raise ValueError("fertility_schedule must contain 'female_pop' and 'births' columns.")
        
    df["asfr"] = (df["births"] / df["female_pop"]) * float(per)
    peak_row = df.loc[df["asfr"].idxmax()] if not df.empty else None
    peak_age = peak_row["age_group"] if peak_row is not None else "N/A"
    peak_val = peak_row["asfr"] if peak_row is not None else 0.0
    
    asfr_dict = dict(zip(df["age_group"], df["asfr"]))
    mean_asfr = float(df["asfr"].mean())
    
    res = DemographicMeasureResult(
        code="ASFR",
        name="Age-Specific Fertility Rate Schedule",
        block="C: Fertility",
        raw_value=peak_val,
        formatted_value=f"Peak: {peak_val:.1f} per {per:,} (Age {peak_age})",
        unit=f"births per {per:,} women in age group",
        formula=f"ASFR_i = (Births_i / Women_i) * {per}",
        citation="Preston et al. (2001), Ch. 5; Newell (1988), Ch. 4",
        inputs_used={
            "asfr_schedule": asfr_dict,
            "peak_age_group": peak_age,
            "peak_asfr": peak_val,
            "mean_asfr": mean_asfr,
        },
        notes="Reveals the age pattern of childbearing; peak is typically in 20-24 or 25-29 age groups."
    )
    return res, df


def calculate_total_fertility_rate(
    fertility_schedule_or_asfrs: Union[pd.DataFrame, List[float], Dict[str, float]],
    age_interval: int = 5,
) -> DemographicMeasureResult:
    """
    Calculate Total Fertility Rate (TFR).
    TFR = (interval * sum(ASFR_i)) / 1000 = interval * sum(Births_i / Women_i)
    
    Formula: TFR = 5 * sum(ASFR_i / 1000)
    """
    if isinstance(fertility_schedule_or_asfrs, pd.DataFrame):
        df = fertility_schedule_or_asfrs
        if "asfr" in df.columns:
            sum_asfr = df["asfr"].sum()
        elif "births" in df.columns and "female_pop" in df.columns:
            sum_asfr = (df["births"] / df["female_pop"] * 1000.0).sum()
        else:
            raise ValueError("DataFrame must contain 'asfr' or ('births' and 'female_pop').")
        tfr_val = (age_interval * sum_asfr) / 1000.0
    elif isinstance(fertility_schedule_or_asfrs, dict):
        sum_asfr = sum(fertility_schedule_or_asfrs.values())
        tfr_val = (age_interval * sum_asfr) / 1000.0
    elif isinstance(fertility_schedule_or_asfrs, (list, np.ndarray)):
        sum_asfr = sum(fertility_schedule_or_asfrs)
        tfr_val = (age_interval * sum_asfr) / 1000.0
    else:
        raise TypeError("Unsupported format for fertility schedule.")
        
    return DemographicMeasureResult(
        code="TFR",
        name="Total Fertility Rate",
        block="C: Fertility",
        raw_value=tfr_val,
        formatted_value=f"{tfr_val:.2f} children per woman",
        unit="children per woman",
        formula=f"TFR = {age_interval} * sum(ASFR_i) / 1000",
        citation="Preston et al. (2001), Ch. 5; UN DESA Population Division",
        inputs_used={
            "sum_asfr": sum_asfr,
            "age_interval": age_interval,
        },
        notes="Replacement-level fertility in low-mortality countries is ~2.1 children per woman."
    )


def calculate_gross_reproduction_rate(
    tfr: Optional[float] = None,
    fertility_schedule: Optional[pd.DataFrame] = None,
    female_birth_proportion: float = 100.0 / 205.0,  # ~0.4878 (standard SRB ~ 105 M : 100 F)
    age_interval: int = 5,
) -> DemographicMeasureResult:
    """
    Calculate Gross Reproduction Rate (GRR).
    GRR = TFR * (Female Births / Total Births)
    Or GRR = age_interval * sum(ASFR_female_i) / 1000
    
    Formula: GRR = TFR * (B_f / B_t)
    """
    if fertility_schedule is not None and "female_births" in fertility_schedule.columns and "female_pop" in fertility_schedule.columns:
        sum_f_asfr = (fertility_schedule["female_births"] / fertility_schedule["female_pop"] * 1000.0).sum()
        grr_val = (age_interval * sum_f_asfr) / 1000.0
    elif tfr is not None:
        grr_val = tfr * female_birth_proportion
    elif fertility_schedule is not None and "births" in fertility_schedule.columns and "female_pop" in fertility_schedule.columns:
        tfr_res = calculate_total_fertility_rate(fertility_schedule, age_interval)
        grr_val = tfr_res.raw_value * female_birth_proportion
    else:
        raise ValueError("Either TFR or a valid fertility_schedule must be provided.")
        
    return DemographicMeasureResult(
        code="GRR",
        name="Gross Reproduction Rate",
        block="C: Fertility",
        raw_value=grr_val,
        formatted_value=f"{grr_val:.3f} daughters per woman",
        unit="daughters per woman",
        formula=f"GRR = TFR * (B_f / B_t) [assuming sex ratio at birth ~ 105]",
        citation="Preston et al. (2001), Ch. 5; Rowland (2003), Ch. 7",
        inputs_used={
            "tfr": tfr,
            "female_birth_proportion": female_birth_proportion,
            "age_interval": age_interval,
        },
        notes="Average number of daughters born per woman if she survives the entire reproductive span."
    )


def calculate_net_reproduction_rate(
    grr: Optional[float] = None,
    tfr: Optional[float] = None,
    fertility_schedule: Optional[pd.DataFrame] = None,
    life_table_female: Optional[pd.DataFrame] = None,
    female_survival_to_childbearing: float = 0.965,  # Heuristic fallback if life table not provided
    female_birth_proportion: float = 100.0 / 205.0,
    age_interval: int = 5,
    radix: float = 100000.0,
) -> DemographicMeasureResult:
    """
    Calculate Net Reproduction Rate (NRR).
    If female life table fragment ({}_nL_x) is provided:
        NRR = sum( (Births_female_i / Women_i) * (nLx_i / (5 * l_0)) )
    Else:
        NRR approx = GRR * p_survival_to_mean_age_of_childbearing
    
    Formula: NRR = sum( ASFR_f,i * (nLx / (n * l0)) )
    """
    method = "approximate_survival"
    
    if (fertility_schedule is not None) and (life_table_female is not None) and ("nLx" in life_table_female.columns):
        # Precise cohort-survival derivation
        df = pd.merge(fertility_schedule, life_table_female, on="age_group", how="inner")
        if not df.empty:
            f_birth_col = "female_births" if "female_births" in df.columns else None
            if f_birth_col:
                nrr_val = float((df[f_birth_col] / df["female_pop"] * (df["nLx"] / (age_interval * radix)) * age_interval).sum())
            else:
                nrr_val = float((df["births"] * female_birth_proportion / df["female_pop"] * (df["nLx"] / (age_interval * radix)) * age_interval).sum())
            method = "life_table_survival_integration"
        else:
            base_grr = grr if grr is not None else (tfr * female_birth_proportion if tfr is not None else calculate_gross_reproduction_rate(fertility_schedule=fertility_schedule).raw_value)
            nrr_val = base_grr * female_survival_to_childbearing
    else:
        if grr is None:
            if tfr is not None:
                grr = tfr * female_birth_proportion
            elif fertility_schedule is not None:
                grr = calculate_gross_reproduction_rate(fertility_schedule=fertility_schedule).raw_value
            else:
                raise ValueError("Must provide either GRR, TFR, or fertility schedule.")
        nrr_val = grr * female_survival_to_childbearing
        
    return DemographicMeasureResult(
        code="NRR",
        name="Net Reproduction Rate",
        block="C: Fertility",
        raw_value=nrr_val,
        formatted_value=f"{nrr_val:.3f} surviving daughters per woman",
        unit="surviving daughters per woman",
        formula="NRR = sum( ASFR_f,i * (nLx / (n * l0)) )",
        citation="Preston et al. (2001), Ch. 5; Bhende & Kanitkar (2010), Ch. 8",
        inputs_used={
            "grr": grr,
            "method": method,
            "female_survival_rate_used": female_survival_to_childbearing if method == "approximate_survival" else "empirical_nLx",
        },
        notes="Exact replacement level is NRR = 1.0. If NRR > 1, population grows; if NRR < 1, population contracts long-term."
    )


def compute_block_c(dataset: DemographicDataset) -> Dict[str, DemographicMeasureResult]:
    """Compute all Block C fertility measures from a demographic dataset."""
    results: Dict[str, DemographicMeasureResult] = {}
    
    b_tot = dataset.total_live_births
    t_pop = dataset.total_population
    
    # 8. CBR
    if b_tot is not None and t_pop is not None:
        results["CBR"] = calculate_crude_birth_rate(b_tot, t_pop)
        
    # 9. MBR
    m_births = dataset.marital_births if dataset.marital_births is not None else b_tot
    m_women = dataset.married_women_15_49
    if m_births is not None and m_women is not None:
        results["MBR"] = calculate_marital_birth_rate(m_births, m_women)
        
    # 10. GFR
    w_15_49 = dataset.total_women_15_49
    if w_15_49 is None and dataset.fertility_schedule is not None and "female_pop" in dataset.fertility_schedule.columns:
        w_15_49 = float(dataset.fertility_schedule["female_pop"].sum())
        
    if b_tot is not None and w_15_49 is not None:
        results["GFR"] = calculate_general_fertility_rate(b_tot, w_15_49)
        
    # 11. ASFR & 12. TFR
    tfr_val = None
    if dataset.fertility_schedule is not None:
        asfr_res, asfr_df = calculate_age_specific_fertility_rates(dataset.fertility_schedule)
        results["ASFR"] = asfr_res
        
        tfr_res = calculate_total_fertility_rate(asfr_df)
        results["TFR"] = tfr_res
        tfr_val = tfr_res.raw_value
        
    # 13. GRR
    grr_val = None
    if tfr_val is not None:
        grr_res = calculate_gross_reproduction_rate(tfr=tfr_val, fertility_schedule=dataset.fertility_schedule)
        results["GRR"] = grr_res
        grr_val = grr_res.raw_value
        
    # 14. NRR
    if grr_val is not None:
        nrr_res = calculate_net_reproduction_rate(
            grr=grr_val,
            tfr=tfr_val,
            fertility_schedule=dataset.fertility_schedule,
            life_table_female=dataset.life_table_female
        )
        results["NRR"] = nrr_res
        
    return results
