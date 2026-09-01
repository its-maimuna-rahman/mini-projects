"""
Missing-Column & Data Gap Assistant (LLM & Rule-Based Demography Expert)
Explains missing demographic columns, why they are required for specific measures,
and provides clear formatting instructions and mathematical alternatives.
"""

from __future__ import annotations
import os
from typing import Dict, Any, List, Optional


COLUMN_EXPLANATIONS: Dict[str, Dict[str, str]] = {
    "male_population": {
        "title": "Male Population Count",
        "affected_measures": "Masculinity Proportion (MP), Sex Ratio (SR), Excess of Males",
        "rationale": "Demographers require separate male counts to measure biological gender balance, male deficit from conflict/migration, or female sex-selection bias.",
        "how_to_fix": "Provide a single total count of males, or include a 'male' column in your single-year or 5-year age table."
    },
    "female_population": {
        "title": "Female Population Count",
        "affected_measures": "Sex Ratio (SR), Excess of Males",
        "rationale": "Required as the demographic base (denominator) to evaluate sex ratios per 100 females.",
        "how_to_fix": "Provide a female total count or include a 'female' column in your age table."
    },
    "pop_0_14": {
        "title": "Child / Youth Population (Ages 0–14)",
        "affected_measures": "Age Composition Ratio (ACR), Total Dependency Ratio (TDR), Child Dependency Ratio (CDR_child)",
        "rationale": "Defines the non-working youthful dependent cohort to gauge future school-age demand and familial dependency burden.",
        "how_to_fix": "Provide the sum of population aged 0 to 14, or provide a 5-year table with '0-4', '5-9', and '10-14' brackets."
    },
    "pop_15_64": {
        "title": "Working-Age Population (Ages 15–64)",
        "affected_measures": "Total Dependency Ratio (TDR), Child Dependency (CDR_child), Old-Age Dependency (OADR), Demographic Dividend Window",
        "rationale": "The economic productive core of a society. The size of this cohort relative to youth and elderly determines the demographic dividend.",
        "how_to_fix": "Provide total population between ages 15 and 64 inclusive."
    },
    "pop_65_plus": {
        "title": "Elderly Population (Ages 65+)",
        "affected_measures": "Old-Age Dependency Ratio (OADR), Total Dependency Ratio (TDR), Aging Index",
        "rationale": "Identifies the retired/pension-eligible demographic group to assess social security sustainability and long-term healthcare demands.",
        "how_to_fix": "Provide the total population count aged 65 and older."
    },
    "total_live_births": {
        "title": "Annual Live Births",
        "affected_measures": "Crude Birth Rate (CBR), General Fertility Rate (GFR), Infant Mortality Rate (IMR), Neonatal Mortality Rate (NMR)",
        "rationale": "The primary numerator for annual fertility and the indispensable denominator for infant and neonatal survival rates.",
        "how_to_fix": "Provide total registered or estimated live births occurring during the census/calendar year."
    },
    "married_women_15_49": {
        "title": "Married Women of Reproductive Age (15–49)",
        "affected_measures": "Marital Birth Rate (MBR / GMFR)",
        "rationale": "Distinguishes legitimate marital fertility pressure from total population exposure, filtering out single/unmarried women.",
        "how_to_fix": "Include total married or in-union women aged 15 to 49 from census marital status tables."
    },
    "total_women_15_49": {
        "title": "Women of Reproductive Age (15–49)",
        "affected_measures": "General Fertility Rate (GFR)",
        "rationale": "Restricts the denominator strictly to the biological childbearing cohort rather than the total general population.",
        "how_to_fix": "Provide female population sum between 15 and 49 years."
    },
    "fertility_schedule": {
        "title": "Age-Specific Fertility Schedule (5-Year Maternal Age Groups)",
        "affected_measures": "Age-Specific Fertility Rate (ASFR), Total Fertility Rate (TFR), Gross Reproduction Rate (GRR), Net Reproduction Rate (NRR)",
        "rationale": "Without maternal age-specific birth counts, it is mathematically impossible to calculate TFR (children per woman) and generational reproduction rates (GRR/NRR) without crude synthetic modeling.",
        "how_to_fix": "Upload a table with columns: 'age_group' (15-19, 20-24, ..., 45-49), 'female_pop', and 'births'."
    },
    "total_deaths": {
        "title": "Annual Total Deaths",
        "affected_measures": "Crude Death Rate (CDR), Corrected CDR, Standardized Mortality Ratio (SMR)",
        "rationale": "Required to measure national mortality intensity and total life loss per 1,000 mid-year inhabitants.",
        "how_to_fix": "Provide annual registered or survey-estimated death total."
    },
    "neonatal_deaths": {
        "title": "Neonatal Deaths (< 28 Days)",
        "affected_measures": "Neonatal Mortality Rate (NMR)",
        "rationale": "Key clinical benchmark for quality of obstetric care, sterile delivery, and newborn resuscitation (SDG 3.2 target).",
        "how_to_fix": "Provide deaths of infants dying in the first 28 days of life."
    },
    "infant_deaths": {
        "title": "Infant Deaths (< 1 Year)",
        "affected_measures": "Infant Mortality Rate (IMR)",
        "rationale": "Universal standard metric of national socioeconomic progress, sanitation, and child survival.",
        "how_to_fix": "Provide annual deaths of infants prior to their first birthday."
    },
    "mortality_schedule": {
        "title": "Age-Specific Mortality Schedule (Population & Deaths by Age)",
        "affected_measures": "Age-Specific Death Rate (ASDR), Direct Standardized Death Rate (DSDR), Standardized Mortality Ratio (SMR)",
        "rationale": "Age-standardization removes the distortion of population aging, allowing true comparisons across countries with different age profiles.",
        "how_to_fix": "Upload a table with columns: 'age_group', 'population', and 'deaths'."
    },
    "pec_omission_rate": {
        "title": "Post-Enumeration Check (PEC) Omission / Completeness Rate",
        "affected_measures": "Corrected CDR, Census Coverage Completeness",
        "rationale": "Raw censuses often under-count remote populations, transient workers, and infants. PEC provides the correction factor.",
        "how_to_fix": "Enter the estimated omission rate (e.g. 0.035 for 3.5% net undercount) or completeness rate (e.g. 0.965)."
    }
}


def explain_missing_gap(
    gap_field: str,
    api_key: Optional[str] = None,
) -> Dict[str, str]:
    """
    Generates a natural, informative explanation for a missing column or field.
    Uses LLM API if key is available, or deterministic demographic engine fallback.
    """
    spec = COLUMN_EXPLANATIONS.get(gap_field)
    if not spec:
        # Generic fallback
        return {
            "title": gap_field.replace("_", " ").title(),
            "affected_measures": "Specific demographic indicators",
            "explanation": f"The input dataset lacks '{gap_field}', which is required for granular demographic rate derivations.",
            "action": "Please include this column or provide an aggregated summary figure."
        }
        
    explanation_text = (
        f"**{spec['title']}** is missing from your uploaded dataset. "
        f"This prevents calculation of **{spec['affected_measures']}**. "
        f"{spec['rationale']} "
        f"\n\n**How to supply this data:** {spec['how_to_fix']}"
    )
    
    # Optional LLM call if API key provided
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if resolved_api_key:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={resolved_api_key}"
            prompt = (
                f"You are a professional demographer. Write a friendly, 2-sentence explanation to a researcher "
                f"explaining why the column '{spec['title']}' is missing and why it is needed to calculate {spec['affected_measures']}."
            )
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            resp = requests.post(url, json=payload, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                llm_text = data["candidates"][0]["content"]["parts"][0]["text"]
                explanation_text = f"{llm_text.strip()}\n\n**Required Format:** {spec['how_to_fix']}"
        except Exception:
            pass  # Seamless fallback to built-in explanation
            
    return {
        "title": spec["title"],
        "affected_measures": spec["affected_measures"],
        "explanation": explanation_text,
        "action": spec["how_to_fix"],
    }
