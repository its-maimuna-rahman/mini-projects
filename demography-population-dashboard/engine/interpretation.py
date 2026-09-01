"""
Demographic Interpretation Layer & Benchmark Standards
Maps all 22 demographic measures to standard global benchmarks (UN, WHO, PRB, CDC),
providing qualitative classifications (Excellent, Good, Moderate, Concerning, Critical),
bell-curve gauge mapping parameters, and plain-language policy narratives.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, List
from engine.base import DemographicMeasureResult


# Authoritative Benchmark Registry with Citations and Sourced Bands
BENCHMARK_REGISTRY: Dict[str, Dict[str, Any]] = {
    "MP": {
        "name": "Masculinity Proportion",
        "unit": "%",
        "source": "UN DESA / Biological Baseline",
        "is_heuristic": False,
        "gauge_range": (45.0, 56.0),
        "bands": [
            {"max": 48.0, "status": "CONCERNING", "label": "Male Deficit (Heavy female surplus / out-migration)", "color": "#4A6B82"},
            {"min": 48.0, "max": 49.5, "status": "MODERATE", "label": "Slight Female Surplus (Aging population)", "color": "#7E9AA8"},
            {"min": 49.5, "max": 51.5, "status": "EXCELLENT", "label": "Balanced Sex Proportion (Normal biological range)", "color": "#CC785C"},
            {"min": 51.5, "max": 53.0, "status": "MODERATE", "label": "Slight Male Surplus (Immigration / high SRB)", "color": "#DDA15E"},
            {"min": 53.0, "status": "CRITICAL", "label": "Severe Male Surplus (Son preference / male labor influx)", "color": "#C05621"}
        ]
    },
    "SR": {
        "name": "Sex Ratio",
        "unit": "males per 100 females",
        "source": "UN Population Division Standards",
        "is_heuristic": False,
        "gauge_range": (85.0, 120.0),
        "bands": [
            {"max": 92.0, "status": "CONCERNING", "label": "Low Sex Ratio (Significant male deficit / war mortality / migration)", "color": "#4A6B82"},
            {"min": 92.0, "max": 97.0, "status": "MODERATE", "label": "Slight Female Excess (Normal in older populations)", "color": "#7E9AA8"},
            {"min": 97.0, "max": 105.0, "status": "EXCELLENT", "label": "Balanced Sex Ratio (Optimal equilibrium)", "color": "#CC785C"},
            {"min": 105.0, "max": 110.0, "status": "MODERATE", "label": "Elevated Male Ratio", "color": "#DDA15E"},
            {"min": 110.0, "status": "CRITICAL", "label": "Skewed Sex Ratio (Severe sex selection or labor migration)", "color": "#C05621"}
        ]
    },
    "EXCESS_M": {
        "name": "Excess of Males",
        "unit": "persons",
        "source": "Demographic Balance Standard",
        "is_heuristic": True,
        "gauge_range": (-5.0, 5.0),  # % excess
        "bands": [
            {"max": -2.0, "status": "MODERATE", "label": "Female Majority", "color": "#7E9AA8"},
            {"min": -2.0, "max": 2.0, "status": "EXCELLENT", "label": "Balanced Gender Distribution", "color": "#CC785C"},
            {"min": 2.0, "status": "MODERATE", "label": "Male Majority", "color": "#DDA15E"}
        ]
    },
    "ACR": {
        "name": "Age Composition Ratio (Working Age %)",
        "unit": "% of total population",
        "source": "UN Demographic Dividend Framework",
        "is_heuristic": False,
        "gauge_range": (45.0, 75.0),
        "bands": [
            {"max": 55.0, "status": "CONCERNING", "label": "High Dependency Burden (Narrow working-age share)", "color": "#C05621"},
            {"min": 55.0, "max": 60.0, "status": "MODERATE", "label": "Moderate Working Share", "color": "#DDA15E"},
            {"min": 60.0, "max": 68.0, "status": "EXCELLENT", "label": "Prime Demographic Dividend Window (Expansive productive base)", "color": "#CC785C"},
            {"min": 68.0, "status": "GOOD", "label": "Peak Productive Ratio (Approaching subsequent aging transition)", "color": "#2A9D8F"}
        ]
    },
    "TDR": {
        "name": "Total Dependency Ratio",
        "unit": "dependents per 100 working-age",
        "source": "World Bank / UN Population Division",
        "is_heuristic": False,
        "gauge_range": (25.0, 100.0),
        "bands": [
            {"max": 45.0, "status": "EXCELLENT", "label": "Low Total Dependency (Optimal economic bonus window)", "color": "#CC785C"},
            {"min": 45.0, "max": 55.0, "status": "GOOD", "label": "Moderate Dependency", "color": "#2A9D8F"},
            {"min": 55.0, "max": 70.0, "status": "MODERATE", "label": "Elevated Dependency Burden", "color": "#DDA15E"},
            {"min": 70.0, "status": "CRITICAL", "label": "High Dependency Load (High economic strain on workers)", "color": "#C05621"}
        ]
    },
    "CDR_CHILD": {
        "name": "Child Dependency Ratio",
        "unit": "children per 100 working-age",
        "source": "UN Population Division",
        "is_heuristic": False,
        "gauge_range": (15.0, 90.0),
        "bands": [
            {"max": 25.0, "status": "GOOD", "label": "Low Youth Dependency (Advanced demographic transition)", "color": "#2A9D8F"},
            {"min": 25.0, "max": 45.0, "status": "EXCELLENT", "label": "Moderate Youth Dependency (Balanced school-age load)", "color": "#CC785C"},
            {"min": 45.0, "max": 65.0, "status": "MODERATE", "label": "High Youth Dependency (Expansive educational investment needed)", "color": "#DDA15E"},
            {"min": 65.0, "status": "CRITICAL", "label": "Heavy Child Dependency Burden (Youth bulge)", "color": "#C05621"}
        ]
    },
    "OADR": {
        "name": "Old-Age Dependency Ratio",
        "unit": "elderly per 100 working-age",
        "source": "OECD / UN Aging Standards",
        "is_heuristic": False,
        "gauge_range": (5.0, 50.0),
        "bands": [
            {"max": 10.0, "status": "GOOD", "label": "Youthful Population (Minimal pension pressure)", "color": "#2A9D8F"},
            {"min": 10.0, "max": 20.0, "status": "EXCELLENT", "label": "Moderate Aging (Sustainable elder support)", "color": "#CC785C"},
            {"min": 20.0, "max": 35.0, "status": "MODERATE", "label": "Aging Society (Growing healthcare/pension liability)", "color": "#DDA15E"},
            {"min": 35.0, "status": "CRITICAL", "label": "Hyper-Aged Society (Severe pension & care workforce deficit)", "color": "#C05621"}
        ]
    },
    "CBR": {
        "name": "Crude Birth Rate",
        "unit": "births per 1,000",
        "source": "UN Demographic Yearbook",
        "is_heuristic": False,
        "gauge_range": (5.0, 45.0),
        "bands": [
            {"max": 10.0, "status": "CONCERNING", "label": "Very Low CBR (Population decline trajectory)", "color": "#C05621"},
            {"min": 10.0, "max": 16.0, "status": "GOOD", "label": "Low CBR (Developed demographic regime)", "color": "#2A9D8F"},
            {"min": 16.0, "max": 25.0, "status": "EXCELLENT", "label": "Moderate CBR (Sustainable replacement pace)", "color": "#CC785C"},
            {"min": 25.0, "max": 35.0, "status": "MODERATE", "label": "High CBR (Rapid population expansion)", "color": "#DDA15E"},
            {"min": 35.0, "status": "CONCERNING", "label": "Very High CBR (High maternal/child health demand)", "color": "#C05621"}
        ]
    },
    "MBR": {
        "name": "Marital Birth Rate",
        "unit": "births per 1,000 married women",
        "source": "Bhende & Kanitkar Demographic Standard",
        "is_heuristic": True,
        "gauge_range": (40.0, 250.0),
        "bands": [
            {"max": 80.0, "status": "GOOD", "label": "Low Marital Fertility (Widespread family planning)", "color": "#2A9D8F"},
            {"min": 80.0, "max": 140.0, "status": "EXCELLENT", "label": "Moderate Marital Fertility", "color": "#CC785C"},
            {"min": 140.0, "max": 200.0, "status": "MODERATE", "label": "Elevated Marital Fertility", "color": "#DDA15E"},
            {"min": 200.0, "status": "CONCERNING", "label": "High Marital Fertility (Natural fertility regime)", "color": "#C05621"}
        ]
    },
    "GFR": {
        "name": "General Fertility Rate",
        "unit": "births per 1,000 women (15-49)",
        "source": "CDC / National Vital Statistics System",
        "is_heuristic": False,
        "gauge_range": (30.0, 180.0),
        "bands": [
            {"max": 50.0, "status": "CONCERNING", "label": "Very Low GFR", "color": "#C05621"},
            {"min": 50.0, "max": 75.0, "status": "GOOD", "label": "Low GFR (Sub-replacement range)", "color": "#2A9D8F"},
            {"min": 75.0, "max": 110.0, "status": "EXCELLENT", "label": "Optimal GFR (Near replacement equilibrium)", "color": "#CC785C"},
            {"min": 110.0, "status": "MODERATE", "label": "High GFR", "color": "#DDA15E"}
        ]
    },
    "ASFR": {
        "name": "Age-Specific Fertility Rate",
        "unit": "births per 1,000 in age group",
        "source": "UN Population Division",
        "is_heuristic": True,
        "gauge_range": (0.0, 250.0),
        "bands": [
            {"max": 100.0, "status": "GOOD", "label": "Controlled Peak Fertility", "color": "#2A9D8F"},
            {"min": 100.0, "max": 180.0, "status": "EXCELLENT", "label": "Moderate Peak Fertility", "color": "#CC785C"},
            {"min": 180.0, "status": "MODERATE", "label": "Concentrated High Peak Fertility", "color": "#DDA15E"}
        ]
    },
    "TFR": {
        "name": "Total Fertility Rate",
        "unit": "children per woman",
        "source": "UN DESA Population Division (Replacement Level = 2.1)",
        "is_heuristic": False,
        "gauge_range": (0.8, 6.0),
        "bands": [
            {"max": 1.3, "status": "CRITICAL", "label": "Lowest-Low Fertility (Severe long-term contraction)", "color": "#C05621"},
            {"min": 1.3, "max": 1.8, "status": "CONCERNING", "label": "Sub-Replacement Fertility (Aging trajectory)", "color": "#DDA15E"},
            {"min": 1.8, "max": 2.2, "status": "EXCELLENT", "label": "Replacement Level (~2.1 children per woman, stable population)", "color": "#CC785C"},
            {"min": 2.2, "max": 3.5, "status": "GOOD", "label": "Moderate Growth Fertility", "color": "#2A9D8F"},
            {"min": 3.5, "status": "CONCERNING", "label": "High Fertility (Rapid population expansion)", "color": "#C05621"}
        ]
    },
    "GRR": {
        "name": "Gross Reproduction Rate",
        "unit": "daughters per woman",
        "source": "Preston et al. Demography Standard",
        "is_heuristic": False,
        "gauge_range": (0.4, 3.0),
        "bands": [
            {"max": 0.9, "status": "CONCERNING", "label": "Sub-Replacement Generation (< 1 daughter per woman)", "color": "#C05621"},
            {"min": 0.9, "max": 1.1, "status": "EXCELLENT", "label": "Generational Replacement (~1.0 daughter per woman)", "color": "#CC785C"},
            {"min": 1.1, "status": "GOOD", "label": "Expanding Female Cohort", "color": "#2A9D8F"}
        ]
    },
    "NRR": {
        "name": "Net Reproduction Rate",
        "unit": "surviving daughters per woman",
        "source": "UN Population Division (Exact Replacement = 1.0)",
        "is_heuristic": False,
        "gauge_range": (0.4, 2.5),
        "bands": [
            {"max": 0.75, "status": "CRITICAL", "label": "Severe Sub-Replacement (NRR << 1.0, rapid generational shrink)", "color": "#C05621"},
            {"min": 0.75, "max": 0.95, "status": "CONCERNING", "label": "Below Replacement (NRR < 1.0)", "color": "#DDA15E"},
            {"min": 0.95, "max": 1.05, "status": "EXCELLENT", "label": "Exact Long-Term Replacement (NRR ≈ 1.0, steady state)", "color": "#CC785C"},
            {"min": 1.05, "max": 1.50, "status": "GOOD", "label": "Moderate Generational Growth", "color": "#2A9D8F"},
            {"min": 1.50, "status": "MODERATE", "label": "Rapid Generational Growth", "color": "#DDA15E"}
        ]
    },
    "CDR": {
        "name": "Crude Death Rate",
        "unit": "deaths per 1,000",
        "source": "WHO Global Health Observatory",
        "is_heuristic": False,
        "gauge_range": (3.0, 20.0),
        "bands": [
            {"max": 6.0, "status": "GOOD", "label": "Low CDR (Youthful population or excellent health systems)", "color": "#2A9D8F"},
            {"min": 6.0, "max": 9.0, "status": "EXCELLENT", "label": "Moderate / Normal CDR", "color": "#CC785C"},
            {"min": 9.0, "max": 13.0, "status": "MODERATE", "label": "Elevated CDR (Often driven by older age structure)", "color": "#DDA15E"},
            {"min": 13.0, "status": "CRITICAL", "label": "High CDR (High epidemiologic burden or extreme aging)", "color": "#C05621"}
        ]
    },
    "CORRECTED_CDR": {
        "name": "Corrected Crude Death Rate",
        "unit": "deaths per 1,000 (adjusted)",
        "source": "UN Vital Statistics Guidelines",
        "is_heuristic": False,
        "gauge_range": (3.0, 25.0),
        "bands": [
            {"max": 7.0, "status": "GOOD", "label": "Low Adjusted Mortality", "color": "#2A9D8F"},
            {"min": 7.0, "max": 10.0, "status": "EXCELLENT", "label": "Normal Adjusted Mortality", "color": "#CC785C"},
            {"min": 10.0, "status": "MODERATE", "label": "Elevated Adjusted Mortality", "color": "#DDA15E"}
        ]
    },
    "NMR": {
        "name": "Neonatal Mortality Rate",
        "unit": "deaths per 1,000 live births",
        "source": "WHO / UN SDG Target 3.2 (Goal: <= 12 per 1,000)",
        "is_heuristic": False,
        "gauge_range": (1.0, 45.0),
        "bands": [
            {"max": 5.0, "status": "EXCELLENT", "label": "Very Low (High-income clinical standard)", "color": "#CC785C"},
            {"min": 5.0, "max": 12.0, "status": "GOOD", "label": "SDG Target Achieved (<= 12.0 per 1,000)", "color": "#2A9D8F"},
            {"min": 12.0, "max": 25.0, "status": "CONCERNING", "label": "Elevated Neonatal Mortality (Above SDG Target)", "color": "#DDA15E"},
            {"min": 25.0, "status": "CRITICAL", "label": "Critical Neonatal Mortality (Urgent delivery/NICU intervention required)", "color": "#C05621"}
        ]
    },
    "IMR": {
        "name": "Infant Mortality Rate",
        "unit": "deaths per 1,000 live births",
        "source": "UNICEF / WHO Global Standards",
        "is_heuristic": False,
        "gauge_range": (1.5, 90.0),
        "bands": [
            {"max": 6.0, "status": "EXCELLENT", "label": "Exceptional Child Health (< 6 per 1,000)", "color": "#CC785C"},
            {"min": 6.0, "max": 15.0, "status": "GOOD", "label": "Low IMR (Good public health and sanitation)", "color": "#2A9D8F"},
            {"min": 15.0, "max": 35.0, "status": "MODERATE", "label": "Moderate IMR", "color": "#DDA15E"},
            {"min": 35.0, "max": 60.0, "status": "CONCERNING", "label": "High IMR (Elevated preventable infant mortality)", "color": "#E76F51"},
            {"min": 60.0, "status": "CRITICAL", "label": "Critical IMR (Severe health/nutrition crisis)", "color": "#C05621"}
        ]
    },
    "CMR": {
        "name": "Child Mortality Rate (U5MR)",
        "unit": "deaths per 1,000 live births",
        "source": "WHO / UN SDG Target 3.2.1 (Goal: <= 25 per 1,000)",
        "is_heuristic": False,
        "gauge_range": (2.0, 120.0),
        "bands": [
            {"max": 8.0, "status": "EXCELLENT", "label": "Very Low Child Mortality", "color": "#CC785C"},
            {"min": 8.0, "max": 25.0, "status": "GOOD", "label": "SDG Target Achieved (<= 25 per 1,000)", "color": "#2A9D8F"},
            {"min": 25.0, "max": 50.0, "status": "CONCERNING", "label": "Elevated Child Mortality", "color": "#DDA15E"},
            {"min": 50.0, "status": "CRITICAL", "label": "High Child Mortality", "color": "#C05621"}
        ]
    },
    "ASDR": {
        "name": "Age-Specific Death Rate",
        "unit": "deaths per 1,000 in age group",
        "source": "WHO Mortality Database",
        "is_heuristic": True,
        "gauge_range": (0.5, 30.0),
        "bands": [
            {"max": 5.0, "status": "EXCELLENT", "label": "Low Baseline Age Mortality", "color": "#CC785C"},
            {"min": 5.0, "max": 10.0, "status": "GOOD", "label": "Moderate Baseline Mortality", "color": "#2A9D8F"},
            {"min": 10.0, "status": "MODERATE", "label": "Elevated Baseline Mortality", "color": "#DDA15E"}
        ]
    },
    "DSDR": {
        "name": "Direct Standardized Death Rate",
        "unit": "standardized deaths per 1,000",
        "source": "WHO Global Standardized Mortality Database",
        "is_heuristic": False,
        "gauge_range": (3.0, 20.0),
        "bands": [
            {"max": 5.5, "status": "EXCELLENT", "label": "Low Age-Standardized Mortality (High life expectancy)", "color": "#CC785C"},
            {"min": 5.5, "max": 8.5, "status": "GOOD", "label": "Moderate Age-Standardized Mortality", "color": "#2A9D8F"},
            {"min": 8.5, "max": 12.0, "status": "MODERATE", "label": "Elevated Age-Standardized Mortality", "color": "#DDA15E"},
            {"min": 12.0, "status": "CRITICAL", "label": "High Age-Standardized Mortality (High premature mortality burden)", "color": "#C05621"}
        ]
    },
    "SMR": {
        "name": "Standardized Mortality Ratio",
        "unit": "ratio (Obs / Exp)",
        "source": "Epidemiologic Standard (Null = 1.00)",
        "is_heuristic": False,
        "gauge_range": (0.5, 2.0),
        "bands": [
            {"max": 0.85, "status": "EXCELLENT", "label": "Substantially Lower Mortality than Standard (SMR < 0.85)", "color": "#CC785C"},
            {"min": 0.85, "max": 1.15, "status": "GOOD", "label": "Comparable to Standard Mortality (0.85 - 1.15)", "color": "#2A9D8F"},
            {"min": 1.15, "max": 1.40, "status": "MODERATE", "label": "Elevated Relative Mortality (15-40% excess deaths)", "color": "#DDA15E"},
            {"min": 1.40, "status": "CRITICAL", "label": "Severe Excess Mortality (> 40% excess deaths over expected)", "color": "#C05621"}
        ]
    },
    "ISDR": {
        "name": "Indirect Standardized Death Rate",
        "unit": "deaths per 1,000",
        "source": "Epidemiologic Standard",
        "is_heuristic": False,
        "gauge_range": (3.0, 20.0),
        "bands": [
            {"max": 6.0, "status": "EXCELLENT", "label": "Low Indirect Standardized Rate", "color": "#CC785C"},
            {"min": 6.0, "max": 9.0, "status": "GOOD", "label": "Moderate Indirect Rate", "color": "#2A9D8F"},
            {"min": 9.0, "status": "MODERATE", "label": "Elevated Indirect Rate", "color": "#DDA15E"}
        ]
    }
}


def interpret_measure(result: DemographicMeasureResult) -> DemographicMeasureResult:
    """Attaches benchmark classification, status rating, gauge parameters, and narrative to result."""
    code = result.code
    val = result.raw_value
    
    spec = BENCHMARK_REGISTRY.get(code)
    if not spec:
        result.interpretation = {
            "status": "UNRATED",
            "label": "Custom Measure",
            "source": "Custom",
            "is_heuristic": True,
            "gauge_min": 0.0,
            "gauge_max": val * 1.5 if val > 0 else 100.0,
            "current_val": val,
        }
        return result
        
    bands = spec["bands"]
    matched_band = None
    for b in bands:
        min_v = b.get("min", -float("inf"))
        max_v = b.get("max", float("inf"))
        if min_v <= val < max_v:
            matched_band = b
            break
            
    if matched_band is None and bands:
        matched_band = bands[-1] if val >= bands[-1].get("min", 0) else bands[0]
        
    g_min, g_max = spec["gauge_range"]
    
    result.interpretation = {
        "status": matched_band.get("status", "MODERATE"),
        "label": matched_band.get("label", "Standard"),
        "color": matched_band.get("color", "#CC785C"),
        "source": spec["source"],
        "is_heuristic": spec["is_heuristic"],
        "gauge_min": g_min,
        "gauge_max": g_max,
        "current_val": val,
        "unit": spec["unit"],
    }
    return result
