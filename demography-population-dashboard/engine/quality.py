"""
Data Quality Module: Demographic Quality Checks & Schema Validation
Implements:
1. Whipple's Index (Digit preference for 0 and 5, ages 23-62)
2. Myers' Blended Index (Digit preference across all digits 0-9)
3. Age Heaping & Anomaly Detection (Sex differentials, infant under-enumeration)
4. Post-Enumeration Check (PEC) Dual System Estimation & Completeness Modeling
5. Missing-Column & Requirement Validation Detector

References:
- United Nations (1955). Manual II: Methods of Appraisal of Quality of Basic Data for Population Estimates.
- Myers, R. J. (1940). Errors and Bias in the Reporting of Ages in Census Data. Transactions of the Actuarial Society of America.
- Chandrasekaran, C., & Deming, W. E. (1949). On a Method of Estimating Birth and Death Rates and the Extent of Registration.
- US Census Bureau (2014). Census Coverage Measurement / Post-Enumeration Survey Methods.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple, Set
import numpy as np
import pandas as pd
from engine.base import QualityCheckResult, DemographicDataset


def calculate_whipples_index(
    single_year_df: pd.DataFrame,
    age_col: str = "age",
    pop_col: str = "total",
    start_age: int = 23,
    end_age: int = 62,
) -> QualityCheckResult:
    """
    Calculate Whipple's Index for age heaping on terminal digits 0 and 5.
    
    Formula:
    W = ( Sum(P_x for x in 25, 30, ..., 60) / ( (1/5) * Sum(P_y for y in 23..62) ) ) * 100
    
    UN Standard Scale:
    - < 105: Highly accurate
    - 105 - 109.9: Fairly accurate
    - 110 - 124.9: Approximate
    - 125 - 174.9: Rough
    - >= 175: Very rough
    """
    df = single_year_df.copy()
    if age_col not in df.columns or pop_col not in df.columns:
        if pop_col == "total" and "male" in df.columns and "female" in df.columns:
            df["total"] = df["male"] + df["female"]
        else:
            return QualityCheckResult(
                check_code="WHIPPLE",
                name="Whipple's Index (Age Heaping on 0 and 5)",
                score=None,
                status="MISSING_DATA",
                summary="Single-year age distribution not provided.",
                interpretation="Cannot compute Whipple's Index without single-year age data.",
                recommendation="Provide single-year population data from age 23 to 62."
            )
            
    filtered = df[(df[age_col] >= start_age) & (df[age_col] <= end_age)]
    if len(filtered) < (end_age - start_age + 1):
        # Missing intermediate single years
        pass
        
    total_23_62 = filtered[pop_col].sum()
    if total_23_62 <= 0:
        return QualityCheckResult(
            check_code="WHIPPLE",
            name="Whipple's Index (Age Heaping on 0 and 5)",
            score=None,
            status="MISSING_DATA",
            summary="Zero population recorded in age span 23-62.",
            interpretation="Insufficient data to compute Whipple's Index.",
            recommendation="Verify population counts for ages 23 to 62."
        )
        
    fives_and_zeros = filtered[filtered[age_col] % 5 == 0][pop_col].sum()
    whipple_score = (fives_and_zeros / (0.2 * total_23_62)) * 100.0
    
    if whipple_score < 105.0:
        status = "EXCELLENT"
        interp = "Highly accurate age reporting (negligible digit preference on 0 and 5)."
        recom = "Data is robust for single-year demographic modeling and actuarial tables."
    elif whipple_score < 110.0:
        status = "ACCEPTABLE"
        interp = "Fairly accurate data with minor digit attraction."
        recom = "Standard demographic smoothing is optional but safe to use."
    elif whipple_score < 125.0:
        status = "WARNING"
        interp = "Approximate data showing noticeable preference for terminal digits 0 and 5."
        recom = "Apply Sprague or Beers 5-year graduated multipliers before single-year cohort projection."
    elif whipple_score < 175.0:
        status = "SEVERE"
        interp = "Rough data with substantial age heaping / digit attraction."
        recom = "Strongly recommend aggregating into 5-year age groups and applying Feeney or Carrier-Farrag smoothing."
    else:
        status = "SEVERE"
        interp = "Very rough data exhibiting massive age distortion and clustering around digits 0 and 5."
        recom = "Direct single-year rates cannot be used; rigorous graduation and PEC adjustments mandatory."
        
    return QualityCheckResult(
        check_code="WHIPPLE",
        name="Whipple's Index (Age Heaping on 0 and 5)",
        score=float(whipple_score),
        status=status,
        summary=f"Whipple's Index = {whipple_score:.2f} ({status.title()})",
        interpretation=interp,
        recommendation=recom,
        details={
            "score": float(whipple_score),
            "start_age": start_age,
            "end_age": end_age,
            "population_23_62": float(total_23_62),
            "population_ending_0_5": float(fives_and_zeros),
            "expected_proportion": 0.20,
            "observed_proportion": float(fives_and_zeros / total_23_62),
        }
    )


def calculate_myers_blended_index(
    single_year_df: pd.DataFrame,
    age_col: str = "age",
    pop_col: str = "total",
    start_age: int = 10,
    end_age: int = 69,
) -> QualityCheckResult:
    """
    Calculate Myers' Blended Index for preference across all digits 0 to 9.
    
    Method:
    1. Sum populations by terminal digit for ages 10-69 (Sum 1) and 20-69 (Sum 2).
    2. Blended weight for digit d: (d+1)*Sum1 + (9-d)*Sum2.
    3. Calculate percentage distribution of blended population.
    4. Index = 0.5 * Sum(|%_d - 10.0%|).
    
    Scale: 0 (no heaping) to 90 (all reported at one digit).
    - < 5: Very low preference (accurate)
    - 5 - 10: Moderate preference
    - 10 - 20: Substantial preference
    - > 20: Severe age heaping
    """
    df = single_year_df.copy()
    if age_col not in df.columns or pop_col not in df.columns:
        if pop_col == "total" and "male" in df.columns and "female" in df.columns:
            df["total"] = df["male"] + df["female"]
        else:
            return QualityCheckResult(
                check_code="MYERS",
                name="Myers' Blended Index (All Digits 0-9)",
                score=None,
                status="MISSING_DATA",
                summary="Single-year age distribution not provided.",
                interpretation="Cannot compute Myers' Index without single-year age data.",
                recommendation="Provide single-year population data from age 10 to 69."
            )
            
    filtered = df[(df[age_col] >= start_age) & (df[age_col] <= end_age)]
    if filtered.empty or filtered[pop_col].sum() <= 0:
        return QualityCheckResult(
            check_code="MYERS",
            name="Myers' Blended Index (All Digits 0-9)",
            score=None,
            status="MISSING_DATA",
            summary="Zero population recorded in age span 10-69.",
            interpretation="Insufficient data to compute Myers' Index.",
            recommendation="Verify single-year population counts."
        )
        
    # Sum 1: Ages 10-69 by terminal digit
    df_10_69 = df[(df[age_col] >= 10) & (df[age_col] <= 69)].copy()
    df_10_69["digit"] = df_10_69[age_col] % 10
    sum1 = df_10_69.groupby("digit")[pop_col].sum().to_dict()
    
    # Sum 2: Ages 20-69 by terminal digit
    df_20_69 = df[(df[age_col] >= 20) & (df[age_col] <= 69)].copy()
    df_20_69["digit"] = df_20_69[age_col] % 10
    sum2 = df_20_69.groupby("digit")[pop_col].sum().to_dict()
    
    blended_counts = {}
    for d in range(10):
        s1 = sum1.get(d, 0.0)
        s2 = sum2.get(d, 0.0)
        w1 = d + 1
        w2 = 9 - d
        blended_counts[d] = (w1 * s1) + (w2 * s2)
        
    total_blended = sum(blended_counts.values())
    if total_blended <= 0:
        return QualityCheckResult(
            check_code="MYERS",
            name="Myers' Blended Index",
            score=None,
            status="MISSING_DATA",
            summary="Blended population sum is zero.",
            interpretation="Cannot compute Myers' Index.",
            recommendation="Check data inputs."
        )
        
    blended_pct = {d: (cnt / total_blended) * 100.0 for d, cnt in blended_counts.items()}
    deviations = {d: abs(pct - 10.0) for d, pct in blended_pct.items()}
    myers_index = 0.5 * sum(deviations.values())
    
    # Identify most preferred and avoided digits
    max_digit = max(blended_pct, key=blended_pct.get)
    min_digit = min(blended_pct, key=blended_pct.get)
    
    if myers_index < 5.0:
        status = "EXCELLENT"
        interp = f"Very low digit preference (Myers' Index = {myers_index:.2f}). Age reporting is highly accurate."
        recom = "High confidence in single-year analysis and projections."
    elif myers_index < 10.0:
        status = "ACCEPTABLE"
        interp = f"Moderate digit preference (Myers' Index = {myers_index:.2f}). Preferred digit: '{max_digit}' ({blended_pct[max_digit]:.1f}%)."
        recom = "Standard 5-year groupings recommended for critical analyses."
    elif myers_index < 20.0:
        status = "WARNING"
        interp = f"Substantial digit preference (Myers' Index = {myers_index:.2f}). Heavy attraction to digit '{max_digit}'."
        recom = "Graduation techniques (e.g. Karup-King or Beers) required before demographic inference."
    else:
        status = "SEVERE"
        interp = f"Severe age heaping (Myers' Index = {myers_index:.2f}). Extreme distortion at digit '{max_digit}' ({blended_pct[max_digit]:.1f}% vs 10% expected)."
        recom = "Single-year data should not be used directly; apply strong mathematical smoothing."
        
    return QualityCheckResult(
        check_code="MYERS",
        name="Myers' Blended Index (All Digits 0-9)",
        score=float(myers_index),
        status=status,
        summary=f"Myers' Index = {myers_index:.2f} ({status.title()})",
        interpretation=interp,
        recommendation=recom,
        details={
            "score": float(myers_index),
            "digit_distribution_pct": blended_pct,
            "digit_deviations": deviations,
            "most_preferred_digit": max_digit,
            "most_avoided_digit": min_digit,
        }
    )


def calculate_pec_comparison(
    census_count: float,
    pec_count: Optional[float] = None,
    matched_count: Optional[float] = None,
    omission_rate: Optional[float] = None,
    name: str = "Post-Enumeration Check (PEC) Coverage Analysis",
) -> QualityCheckResult:
    """
    Evaluate Census Coverage & Completeness using Post-Enumeration Check (PEC)
    or Dual System Estimation (DSE) (Chandra-Deming / Peterson-Lincoln formula).
    
    N_true = (Census_Count * PEC_Count) / Matched_Count
    Omission Rate = (N_true - Census_Count) / N_true
    Completeness = Census_Count / N_true
    """
    if omission_rate is not None:
        omission_pct = omission_rate * 100.0
        comp_rate = 1.0 - omission_rate
        est_true_pop = census_count / comp_rate if comp_rate > 0 else census_count
        method = "Direct Omission Rate Parameter"
    elif pec_count is not None and matched_count is not None and matched_count > 0:
        est_true_pop = (census_count * pec_count) / matched_count
        omission_rate = (est_true_pop - census_count) / est_true_pop if est_true_pop > 0 else 0.0
        omission_pct = omission_rate * 100.0
        comp_rate = census_count / est_true_pop if est_true_pop > 0 else 1.0
        method = "Chandra-Deming Dual System Estimation"
    else:
        # Default nominal PEC check
        return QualityCheckResult(
            check_code="PEC",
            name=name,
            score=None,
            status="MISSING_DATA",
            summary="PEC survey or dual-system data not provided.",
            interpretation="Census coverage completeness cannot be independently benchmarked.",
            recommendation="Provide PEC survey sample counts or net omission rate to calculate corrected vital rates."
        )
        
    net_undercount = est_true_pop - census_count
    
    if omission_pct < 2.0:
        status = "EXCELLENT"
        interp = f"Excellent census coverage ({comp_rate*100:.1f}% completeness, {omission_pct:.2f}% net omission)."
        recom = "Unadjusted census figures are reliable for resource allocation and vital rate denominators."
    elif omission_pct < 5.0:
        status = "ACCEPTABLE"
        interp = f"Acceptable coverage ({comp_rate*100:.1f}% completeness, {omission_pct:.2f}% net omission)."
        recom = "Apply PEC adjustment multiplier k = 1 / C ({1/comp_rate:.4f}) for precision demographic rates."
    elif omission_pct < 10.0:
        status = "WARNING"
        interp = f"Moderate undercount ({omission_pct:.2f}% net omission, ~{net_undercount:,.0f} omitted persons)."
        recom = "Corrected death and birth rates must be used to avoid artificially deflated vital rates."
    else:
        status = "SEVERE"
        interp = f"Severe under-enumeration ({omission_pct:.2f}% net omission). Substantial coverage failure."
        recom = "Full demographic re-weighting and synthetic cohort reconstruction mandatory."
        
    return QualityCheckResult(
        check_code="PEC",
        name=name,
        score=float(omission_pct),
        status=status,
        summary=f"Net Undercount = {omission_pct:.2f}% (Completeness: {comp_rate*100:.1f}%)",
        interpretation=interp,
        recommendation=recom,
        details={
            "census_count": float(census_count),
            "estimated_true_population": float(est_true_pop),
            "net_undercount_persons": float(net_undercount),
            "completeness_rate": float(comp_rate),
            "omission_rate": float(omission_rate),
            "adjustment_factor_k": float(1.0 / comp_rate) if comp_rate > 0 else 1.0,
            "method": method,
        }
    )


# Requirements mapping for all 22 measures
MEASURE_REQUIREMENTS: Dict[str, Dict[str, Any]] = {
    "MP": {
        "name": "Masculinity Proportion",
        "block": "A: Sex Composition",
        "required_fields": ["male_population", "total_population (or female_population)"],
        "purpose": "Computes proportion of males in the total population."
    },
    "SR": {
        "name": "Sex Ratio",
        "block": "A: Sex Composition",
        "required_fields": ["male_population", "female_population"],
        "purpose": "Calculates males per 100 females to assess sex balance."
    },
    "EXCESS_M": {
        "name": "Excess of Males",
        "block": "A: Sex Composition",
        "required_fields": ["male_population", "female_population"],
        "purpose": "Measures absolute and percentage sex surplus."
    },
    "ACR": {
        "name": "Age Composition Ratio",
        "block": "B: Age Composition",
        "required_fields": ["pop_0_14", "pop_15_64", "pop_65_plus (or age_group_5yr / single_year_ages)"],
        "purpose": "Measures share of youth, working-age, and elderly populations."
    },
    "TDR": {
        "name": "Total Dependency Ratio",
        "block": "B: Age Composition",
        "required_fields": ["pop_0_14", "pop_15_64", "pop_65_plus"],
        "purpose": "Measures total dependent load per 100 working-age individuals."
    },
    "CDR_CHILD": {
        "name": "Child Dependency Ratio",
        "block": "B: Age Composition",
        "required_fields": ["pop_0_14", "pop_15_64"],
        "purpose": "Measures youthful economic dependence load."
    },
    "OADR": {
        "name": "Old-Age Dependency Ratio",
        "block": "B: Age Composition",
        "required_fields": ["pop_65_plus", "pop_15_64"],
        "purpose": "Measures elderly support load on working-age cohort."
    },
    "CBR": {
        "name": "Crude Birth Rate",
        "block": "C: Fertility",
        "required_fields": ["total_live_births", "total_population"],
        "purpose": "Measures annual births per 1,000 mid-year population."
    },
    "MBR": {
        "name": "Marital Birth Rate (GMFR)",
        "block": "C: Fertility",
        "required_fields": ["marital_births (or total_live_births)", "married_women_15_49"],
        "purpose": "Measures birth rate among married women of reproductive age."
    },
    "GFR": {
        "name": "General Fertility Rate",
        "block": "C: Fertility",
        "required_fields": ["total_live_births", "total_women_15_49 (or fertility_schedule)"],
        "purpose": "Measures annual births per 1,000 women of childbearing age."
    },
    "ASFR": {
        "name": "Age-Specific Fertility Rate",
        "block": "C: Fertility",
        "required_fields": ["fertility_schedule ('age_group', 'female_pop', 'births')"],
        "purpose": "Measures childbearing schedule across maternal 5-year age groups."
    },
    "TFR": {
        "name": "Total Fertility Rate",
        "block": "C: Fertility",
        "required_fields": ["fertility_schedule (or ASFR series)"],
        "purpose": "Calculates average children born per woman over lifetime."
    },
    "GRR": {
        "name": "Gross Reproduction Rate",
        "block": "C: Fertility",
        "required_fields": ["fertility_schedule (or TFR + sex ratio at birth)"],
        "purpose": "Measures daughters born per woman ignoring maternal mortality."
    },
    "NRR": {
        "name": "Net Reproduction Rate",
        "block": "C: Fertility",
        "required_fields": ["fertility_schedule (or GRR + life table survival)"],
        "purpose": "Measures exact intergenerational replacement of female cohort."
    },
    "CDR": {
        "name": "Crude Death Rate",
        "block": "D: Mortality",
        "required_fields": ["total_deaths", "total_population"],
        "purpose": "Measures annual deaths per 1,000 mid-year population."
    },
    "CORRECTED_CDR": {
        "name": "Corrected Crude Death Rate",
        "block": "D: Mortality",
        "required_fields": ["total_deaths", "total_population", "pec_completeness_rate (or omission_rate)"],
        "purpose": "Adjusts crude mortality rate for under-registration and coverage omissions."
    },
    "NMR": {
        "name": "Neonatal Mortality Rate",
        "block": "D: Mortality",
        "required_fields": ["neonatal_deaths (<28 days)", "total_live_births"],
        "purpose": "Measures early newborn mortality per 1,000 live births."
    },
    "IMR": {
        "name": "Infant Mortality Rate",
        "block": "D: Mortality",
        "required_fields": ["infant_deaths (<1 year)", "total_live_births"],
        "purpose": "Measures mortality under age 1 per 1,000 live births."
    },
    "CMR": {
        "name": "Child Mortality Rate (U5MR)",
        "block": "D: Mortality",
        "required_fields": ["child_deaths_1_4 & pop_1_4 (or infant_deaths & live_births)"],
        "purpose": "Measures under-5 child mortality risk."
    },
    "ASDR": {
        "name": "Age-Specific Death Rate",
        "block": "D: Mortality",
        "required_fields": ["mortality_schedule ('age_group', 'population', 'deaths')"],
        "purpose": "Constructs age-specific mortality schedule across the life course."
    },
    "DSDR": {
        "name": "Direct Standardized Death Rate",
        "block": "D: Mortality",
        "required_fields": ["mortality_schedule", "standard_population (WHO standard included)"],
        "purpose": "Standardizes death rate against standard population age weights."
    },
    "SMR": {
        "name": "Standardized Mortality Ratio & ISDR",
        "block": "D: Mortality",
        "required_fields": ["total_deaths", "mortality_schedule (or standard rates)"],
        "purpose": "Compares observed deaths against expected standard deaths."
    }
}


def validate_dataset_completeness(dataset: DemographicDataset) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Inspects dataset against all 22 measures.
    Returns:
    - computable_measures: List of measure codes that CAN be calculated.
    - missing_measures: List of measure codes that CANNOT be calculated.
    - gap_analysis: Structured report of missing fields, why they matter, and guidance.
    """
    computable: List[str] = []
    missing: List[str] = []
    gap_analysis: Dict[str, Any] = {}
    
    # Block A
    has_m = dataset.male_population is not None or (dataset.single_year_ages is not None and "male" in dataset.single_year_ages.columns)
    has_f = dataset.female_population is not None or (dataset.single_year_ages is not None and "female" in dataset.single_year_ages.columns)
    has_t = dataset.total_population is not None or (has_m and has_f)
    
    if has_m and has_t:
        computable.append("MP")
    else:
        missing.append("MP")
        gap_analysis["MP"] = {"missing_fields": ["male_population", "total_population"], "reason": "Requires male count and total population."}
        
    if has_m and has_f:
        computable.append("SR")
        computable.append("EXCESS_M")
    else:
        missing.extend(["SR", "EXCESS_M"])
        gap_analysis["SR"] = {"missing_fields": ["male_population", "female_population"], "reason": "Requires both male and female population counts."}
        gap_analysis["EXCESS_M"] = {"missing_fields": ["male_population", "female_population"], "reason": "Requires sex-disaggregated counts to compute surplus."}
        
    # Block B
    p_0_14 = dataset.pop_0_14
    p_15_64 = dataset.pop_15_64
    p_65_plus = dataset.pop_65_plus
    if p_0_14 is None or p_15_64 is None or p_65_plus is None:
        if dataset.age_group_5yr is not None or dataset.single_year_ages is not None:
            # Can be derived from tables
            p_0_14, p_15_64, p_65_plus = 1, 1, 1  # placeholder indicating derivation possible
            
    if p_0_14 is not None and p_15_64 is not None and p_65_plus is not None:
        computable.extend(["ACR", "TDR", "CDR_CHILD", "OADR"])
    else:
        missing.extend(["ACR", "TDR", "CDR_CHILD", "OADR"])
        gap_analysis["Block_B"] = {
            "missing_fields": ["pop_0_14", "pop_15_64", "pop_65_plus", "age_distribution"],
            "reason": "Age-structure and dependency metrics require broad age-group counts (0-14, 15-64, 65+) or age schedule."
        }
        
    # Block C
    has_births = dataset.total_live_births is not None
    if has_births and has_t:
        computable.append("CBR")
    else:
        missing.append("CBR")
        gap_analysis["CBR"] = {"missing_fields": ["total_live_births", "total_population"], "reason": "Crude birth rate requires annual live births and mid-year population."}
        
    if dataset.marital_births is not None and dataset.married_women_15_49 is not None:
        computable.append("MBR")
    else:
        missing.append("MBR")
        gap_analysis["MBR"] = {"missing_fields": ["married_women_15_49", "marital_births"], "reason": "Marital fertility requires married women aged 15-49."}
        
    has_w1549 = dataset.total_women_15_49 is not None or (dataset.fertility_schedule is not None and "female_pop" in dataset.fertility_schedule.columns)
    if has_births and has_w1549:
        computable.append("GFR")
    else:
        missing.append("GFR")
        gap_analysis["GFR"] = {"missing_fields": ["total_women_15_49"], "reason": "General fertility rate requires total female population aged 15-49."}
        
    if dataset.fertility_schedule is not None and "female_pop" in dataset.fertility_schedule.columns and "births" in dataset.fertility_schedule.columns:
        computable.extend(["ASFR", "TFR", "GRR", "NRR"])
    else:
        missing.extend(["ASFR", "TFR", "GRR", "NRR"])
        gap_analysis["Fertility_Schedule"] = {
            "missing_fields": ["fertility_schedule (columns: age_group, female_pop, births)"],
            "reason": "Detailed fertility modeling (ASFR, TFR, GRR, NRR) requires maternal 5-year age-specific birth counts."
        }
        
    # Block D
    has_deaths = dataset.total_deaths is not None or (dataset.mortality_schedule is not None and "deaths" in dataset.mortality_schedule.columns)
    if has_deaths and has_t:
        computable.append("CDR")
        computable.append("CORRECTED_CDR")
    else:
        missing.extend(["CDR", "CORRECTED_CDR"])
        gap_analysis["CDR"] = {"missing_fields": ["total_deaths", "total_population"], "reason": "Crude death rate requires total mortality counts and mid-year population."}
        
    if dataset.neonatal_deaths is not None and has_births:
        computable.append("NMR")
    else:
        missing.append("NMR")
        gap_analysis["NMR"] = {"missing_fields": ["neonatal_deaths (<28 days)"], "reason": "Neonatal rate requires deaths occurring under 28 days of age."}
        
    if dataset.infant_deaths is not None and has_births:
        computable.append("IMR")
    else:
        missing.append("IMR")
        gap_analysis["IMR"] = {"missing_fields": ["infant_deaths (<1 year)"], "reason": "Infant mortality rate requires deaths occurring before age 1."}
        
    if (dataset.child_deaths_1_4 is not None and dataset.pop_1_4 is not None) or (dataset.infant_deaths is not None and dataset.child_deaths_1_4 is not None and has_births):
        computable.append("CMR")
    else:
        missing.append("CMR")
        gap_analysis["CMR"] = {"missing_fields": ["child_deaths_1_4", "pop_1_4"], "reason": "Child mortality rate requires deaths and population for age group 1-4."}
        
    if dataset.mortality_schedule is not None and "population" in dataset.mortality_schedule.columns and "deaths" in dataset.mortality_schedule.columns:
        computable.extend(["ASDR", "DSDR", "SMR"])
    else:
        missing.extend(["ASDR", "DSDR", "SMR"])
        gap_analysis["Mortality_Schedule"] = {
            "missing_fields": ["mortality_schedule (columns: age_group, population, deaths)"],
            "reason": "Age-standardization (Direct DSDR, ASDR, Indirect SMR) requires age-specific mortality schedule."
        }
        
    return computable, missing, gap_analysis


def run_all_quality_checks(dataset: DemographicDataset) -> Dict[str, QualityCheckResult]:
    """Runs all data-quality validations on the provided dataset."""
    results: Dict[str, QualityCheckResult] = {}
    
    # 1. Whipple's Index
    if dataset.single_year_ages is not None:
        results["WHIPPLE"] = calculate_whipples_index(dataset.single_year_ages)
    else:
        results["WHIPPLE"] = QualityCheckResult(
            check_code="WHIPPLE",
            name="Whipple's Index (Age Heaping on 0 and 5)",
            score=None,
            status="MISSING_DATA",
            summary="Single-year age distribution not provided.",
            interpretation="Cannot evaluate Whipple's Index without single-year age data.",
            recommendation="Upload a single-year age table (ages 0-100) to check for digit preference on 0 and 5."
        )
        
    # 2. Myers' Blended Index
    if dataset.single_year_ages is not None:
        results["MYERS"] = calculate_myers_blended_index(dataset.single_year_ages)
    else:
        results["MYERS"] = QualityCheckResult(
            check_code="MYERS",
            name="Myers' Blended Index (All Digits 0-9)",
            score=None,
            status="MISSING_DATA",
            summary="Single-year age distribution not provided.",
            interpretation="Cannot evaluate Myers' digit attraction without single-year age data.",
            recommendation="Upload single-year age distribution to compute full 10-digit preference index."
        )
        
    # 3. PEC Post-Enumeration Check
    t_pop = dataset.total_population
    if t_pop is None and dataset.single_year_ages is not None:
        tot_col = "total" if "total" in dataset.single_year_ages.columns else dataset.single_year_ages.columns[1]
        t_pop = float(dataset.single_year_ages[tot_col].sum())
        
    if t_pop is not None and (dataset.pec_omission_rate is not None or dataset.pec_completeness_rate is not None):
        results["PEC"] = calculate_pec_comparison(
            census_count=t_pop,
            omission_rate=dataset.pec_omission_rate if dataset.pec_omission_rate is not None else (1.0 - dataset.pec_completeness_rate if dataset.pec_completeness_rate else None)
        )
    else:
        results["PEC"] = QualityCheckResult(
            check_code="PEC",
            name="Post-Enumeration Check (PEC) Coverage",
            score=None,
            status="MISSING_DATA",
            summary="No PEC or omission rate specified.",
            interpretation="Assuming standard unadjusted enumeration baseline.",
            recommendation="Specify PEC omission rate or completeness percentage to adjust crude rates."
        )
        
    # 4. Missing Column / Schema Completeness Check
    comp, miss, gaps = validate_dataset_completeness(dataset)
    comp_pct = (len(comp) / 22.0) * 100.0
    status_str = "EXCELLENT" if comp_pct == 100 else ("ACCEPTABLE" if comp_pct >= 60 else ("WARNING" if comp_pct >= 30 else "SEVERE"))
    
    results["SCHEMA_CHECK"] = QualityCheckResult(
        check_code="SCHEMA_CHECK",
        name="Dataset Completeness & Measure Readiness",
        score=comp_pct,
        status=status_str,
        summary=f"{len(comp)}/22 measures computable ({comp_pct:.0f}% readiness)",
        interpretation=f"Dataset contains sufficient data to compute {len(comp)} demographic measures. {len(miss)} measures require additional data.",
        recommendation=f"To enable all 22 measures, upload the missing columns identified in the gap analysis.",
        details={
            "computable_count": len(comp),
            "computable_measures": comp,
            "missing_count": len(miss),
            "missing_measures": miss,
            "gap_analysis": gaps,
        }
    )
    
    return results
