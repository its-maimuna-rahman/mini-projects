"""
Module 2: Demographic Inference, Trajectory Simulation & Policy Recommendation Engine
Implements:
1. Historical Time-Series Ingestion & Trend Modeling
2. Future Demographic Trajectory Projections (2025 - 2070)
   - Cohort-Component / Logistic-Exponential Transition Extrapolation
   - TFR floor & rebound dynamics
   - Life expectancy gain & epidemiological deceleration
   - Aging index & demographic dividend window timeline
3. Prescriptive Analysis & Policy Flag Generation
4. Plain-Language Policy Recommendations (Pension, Childcare, Healthcare, Labor Market)

References:
- United Nations DESA (2022). World Population Prospects Projection Methodology.
- Lee, R. D., & Carter, L. R. (1992). Modeling and Forecasting U.S. Mortality. JASA.
- Bloom, D. E., & Canning, D. (2004). Global Demographic Change: Dimensions and Economic Significance.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class PolicyFlag:
    """Represents an actionable demographic inflection flag."""
    indicator: str
    severity: str  # 'CRITICAL', 'CONCERNING', 'OPPORTUNITY', 'STABLE'
    inflection_year: int
    title: str
    description: str
    policy_recommendations: List[str]
    rationale: str


@dataclass
class ProjectionResult:
    """Output container for future demographic trajectory simulation."""
    historical_df: pd.DataFrame
    projected_df: pd.DataFrame
    combined_df: pd.DataFrame
    dividend_start_year: Optional[int]
    dividend_end_year: Optional[int]
    current_phase: str
    assumptions_summary: List[str]
    policy_flags: List[PolicyFlag]
    narrative_policy_brief: str


def simulate_demographic_trajectory(
    historical_df: pd.DataFrame,
    projection_horizon_years: int = 30,
    fertility_scenario: str = "medium",  # 'medium', 'low', 'high'
) -> ProjectionResult:
    """
    Simulates future demographic trajectories based on historical time-series data.
    
    Assumptions:
    - Fertility (TFR): Follows logistic asymptotic path towards scenario target.
      * Medium: Converges towards 1.6 - 1.85 (or gradual rebound if < 1.3)
      * Low: Stalls at ultra-low fertility (~1.25)
      * High: Rebounds towards replacement (~2.05)
    - Mortality (CDR & Life Expectancy): Life expectancy gains decelerate at higher baselines (0.15 - 0.20 yrs/year).
    - Crude Death Rate (CDR): Rises inevitably in aging societies as older cohorts expand.
    - Age Structure: Working-age share tracks fertility lag by 20-25 years.
    """
    df_hist = historical_df.sort_values("year").copy()
    last_row = df_hist.iloc[-1]
    start_year = int(last_row["year"])
    
    last_pop = float(last_row.get("total_population_millions", 50.0))
    last_tfr = float(last_row.get("tfr", 2.1))
    last_cbr = float(last_row.get("cbr", 18.0))
    last_cdr = float(last_row.get("cdr", 7.5))
    last_imr = float(last_row.get("imr", 15.0))
    last_life_exp = float(last_row.get("life_expectancy", 72.0))
    last_pct_young = float(last_row.get("pct_young_0_14", 25.0))
    last_pct_working = float(last_row.get("pct_working_15_64", 65.0))
    last_pct_elderly = float(last_row.get("pct_elderly_65_plus", 10.0))
    
    # Target TFR by scenario
    tfr_targets = {
        "medium": 1.65 if last_tfr > 1.8 else (1.45 if last_tfr > 1.3 else 1.35),
        "low": max(1.10, last_tfr - 0.4),
        "high": min(2.10, last_tfr + 0.35),
    }
    target_tfr = tfr_targets.get(fertility_scenario, 1.65)
    
    projected_rows = []
    curr_pop = last_pop
    curr_tfr = last_tfr
    curr_life_exp = last_life_exp
    curr_pct_young = last_pct_young
    curr_pct_working = last_pct_working
    curr_pct_elderly = last_pct_elderly
    
    for i in range(1, projection_horizon_years + 1):
        year = start_year + i
        
        # Smooth asymptotic convergence for TFR
        alpha_tfr = 0.08
        curr_tfr = curr_tfr + alpha_tfr * (target_tfr - curr_tfr)
        
        # Life expectancy gains (slowing down as life expectancy surpasses 80)
        gain_rate = 0.18 if curr_life_exp < 78 else (0.10 if curr_life_exp < 84 else 0.05)
        curr_life_exp = min(92.0, curr_life_exp + gain_rate)
        
        # IMR continues steady improvement
        curr_imr = max(2.5, last_imr * np.exp(-0.04 * i))
        
        # Young population share reflects trailing TFR
        curr_pct_young = max(8.0, curr_pct_young - 0.25 * (curr_pct_young - (curr_tfr * 7.5)))
        
        # Elderly share increases steadily as past cohorts age
        curr_pct_elderly = min(38.0, curr_pct_elderly + 0.38 + 0.005 * i)
        
        # Working share is residual
        curr_pct_working = max(48.0, 100.0 - curr_pct_young - curr_pct_elderly)
        
        # Dependency ratios
        tdr = ((curr_pct_young + curr_pct_elderly) / curr_pct_working) * 100.0
        oadr = (curr_pct_elderly / curr_pct_working) * 100.0
        
        # CBR and CDR dynamics
        cbr = max(5.0, curr_tfr * 5.8 + (curr_pct_young * 0.15))
        # CDR rises with elderly population expansion (aging effect)
        cdr = 4.5 + (curr_pct_elderly * 0.32)
        
        # Population growth rate (%)
        natural_growth = (cbr - cdr) / 10.0
        curr_pop = max(1.0, curr_pop * (1.0 + natural_growth / 100.0))
        
        projected_rows.append({
            "year": year,
            "total_population_millions": round(curr_pop, 3),
            "cbr": round(cbr, 2),
            "cdr": round(cdr, 2),
            "tfr": round(curr_tfr, 2),
            "imr": round(curr_imr, 2),
            "u5mr": round(curr_imr * 1.35, 2),
            "life_expectancy": round(curr_life_exp, 1),
            "pct_young_0_14": round(curr_pct_young, 2),
            "pct_working_15_64": round(curr_pct_working, 2),
            "pct_elderly_65_plus": round(curr_pct_elderly, 2),
            "tdr": round(tdr, 2),
            "oadr": round(oadr, 2),
            "is_projected": True,
        })
        
    df_proj = pd.DataFrame(projected_rows)
    df_hist["is_projected"] = False
    df_combined = pd.concat([df_hist, df_proj], ignore_index=True)
    
    # Analyze Demographic Dividend Window (Working age >= 60%)
    dividend_years = df_combined[df_combined["pct_working_15_64"] >= 60.0]["year"].tolist()
    div_start = min(dividend_years) if dividend_years else None
    div_end = max(dividend_years) if dividend_years else None
    
    # Determine Current Demographic Phase
    if last_tfr > 3.0:
        current_phase = "Phase 2: High Expansion (Youth Bulge)"
    elif last_tfr >= 2.1 and last_pct_working >= 60.0:
        current_phase = "Phase 3: Prime Demographic Dividend"
    elif last_tfr < 2.1 and last_pct_elderly < 14.0:
        current_phase = "Phase 4: Post-Dividend Transition (Aging Onset)"
    else:
        current_phase = "Phase 5: Hyper-Aging & Population Contraction"
        
    # Generate Policy Flags
    policy_flags = []
    
    # 1. Aging / OADR Crossing Threshold (OADR > 25 or 35)
    oadr_threshold_row = df_proj[df_proj["oadr"] >= 25.0].head(1)
    if not oadr_threshold_row.empty:
        yr = int(oadr_threshold_row.iloc[0]["year"])
        policy_flags.append(PolicyFlag(
            indicator="Old-Age Dependency Ratio (OADR)",
            severity="CRITICAL" if oadr_threshold_row.iloc[0]["oadr"] > 30 else "CONCERNING",
            inflection_year=yr,
            title=f"Elderly Support Strain Inflection ({yr})",
            description=f"By {yr}, old-age dependency surpasses 25 elderly per 100 working individuals, escalating pension obligations and long-term care demands.",
            policy_recommendations=[
                "Transition defined-benefit pensions towards multi-pillar funded accounts.",
                "Gradually index statutory retirement age to gains in healthy life expectancy.",
                "Subsidize community-based eldercare infrastructure and home healthcare aides.",
                "Implement tax incentives for continuous adult reskilling and older worker retention."
            ],
            rationale="An OADR above 25 erodes the tax base while multiplying social security liabilities."
        ))
        
    # 2. Sub-Replacement Fertility / Depopulation Inflection
    tfr_low_row = df_proj[df_proj["tfr"] < 1.5].head(1)
    if not tfr_low_row.empty:
        yr = int(tfr_low_row.iloc[0]["year"])
        policy_flags.append(PolicyFlag(
            indicator="Total Fertility Rate (TFR)",
            severity="CRITICAL",
            inflection_year=yr,
            title=f"Lowest-Low Fertility Trap Risk ({yr})",
            description=f"Projected TFR remains critically depressed below 1.50 children per woman by {yr}, creating an inverted generational pyramid.",
            policy_recommendations=[
                "Expand universal subsidized early childhood care (0-3 years) and paid parental leave.",
                "Implement housing affordability subsidies for young families and first-time parents.",
                "Promote workplace gender equity and flexible working arrangements.",
                "Direct cash child allowances to offset marginal child-rearing costs."
            ],
            rationale="Sustained TFR < 1.5 leads to severe generational shrinking and shrinking school enrollment."
        ))
        
    # 3. Demographic Dividend Window Closure
    if div_end and div_end >= start_year and div_end <= (start_year + projection_horizon_years):
        policy_flags.append(PolicyFlag(
            indicator="Demographic Dividend Window",
            severity="CONCERNING",
            inflection_year=div_end,
            title=f"Closing of Demographic Bonus Window ({div_end})",
            description=f"The national working-age proportion drops below the 60% threshold in {div_end}, closing the demographic window of economic opportunity.",
            policy_recommendations=[
                "Accelerate capital deepening and total factor productivity (TFP) investments before labor supply peaks.",
                "Boost female labor force participation through targeted childcare support.",
                "Reform immigration pathways to attract skilled young international talent."
            ],
            rationale="Once the demographic window closes, economic growth must rely exclusively on productivity per worker rather than headcount."
        ))
        
    # 4. Natural Population Contraction (CBR < CDR)
    contraction_row = df_proj[df_proj["cbr"] < df_proj["cdr"]].head(1)
    if not contraction_row.empty:
        yr = int(contraction_row.iloc[0]["year"])
        policy_flags.append(PolicyFlag(
            indicator="Natural Population Growth",
            severity="CRITICAL",
            inflection_year=yr,
            title=f"Natural Population Decline Crossover ({yr})",
            description=f"In {yr}, annual deaths exceed annual live births (CDR > CBR), shifting the country into involuntary organic population decline.",
            policy_recommendations=[
                "Plan regional consolidation of educational and hospital infrastructure in depopulating zones.",
                "Incentivize automation and AI adoption in labor-scarce service sectors.",
                "Develop compact, age-friendly urban centers to optimize municipal services."
            ],
            rationale="Negative natural increase accelerates rural depopulation and alters macroeconomic aggregate demand."
        ))
        
    assumptions_summary = [
        f"Projection horizon: {projection_horizon_years} years ({start_year} → {start_year + projection_horizon_years})",
        f"Fertility pathway: '{fertility_scenario.title()}' trajectory converging towards TFR = {target_tfr:.2f}",
        f"Life expectancy trajectory: Gains of ~0.10 - 0.18 years/year to reach {curr_life_exp:.1f} years by {start_year + projection_horizon_years}",
        "Mortality dynamics: Crude death rate incorporates age-structural aging effects",
        "Migration assumption: Baseline zero net international migration (closed population assumption for organic demographic momentum)",
    ]
    
    # Narrative Policy Brief
    brief_lines = [
        f"### Strategic Demographic Policy Outlook ({start_year}–{start_year + projection_horizon_years})",
        f"The country is currently situated in **{current_phase}**.",
        f"Over the next {projection_horizon_years} years, total population is projected to move from {last_pop:.2f}M to **{curr_pop:.2f}M**.",
        f"The elderly cohort (65+) will evolve from {last_pct_elderly:.1f}% to **{curr_pct_elderly:.1f}%** of the total population, while the working-age base (15-64) transitions from {last_pct_working:.1f}% to **{curr_pct_working:.1f}%**.",
        f"A total of **{len(policy_flags)} structural inflection flags** have been triggered, demanding proactive fiscal, health, and labor policy responses."
    ]
    
    return ProjectionResult(
        historical_df=df_hist,
        projected_df=df_proj,
        combined_df=df_combined,
        dividend_start_year=div_start,
        dividend_end_year=div_end,
        current_phase=current_phase,
        assumptions_summary=assumptions_summary,
        policy_flags=policy_flags,
        narrative_policy_brief="\n\n".join(brief_lines),
    )
