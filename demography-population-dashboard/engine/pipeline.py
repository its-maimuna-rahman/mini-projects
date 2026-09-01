"""
Master Demographic Pipeline Orchestrator & Comparison Engine
Orchestrates:
1. Ingestion and data cleaning
2. Data quality checks (Whipple, Myers, PEC, Schema validation)
3. Calculation of all 22 demographic measures (Blocks A, B, C, D)
4. Application of the Interpretation Layer (UN/WHO benchmarks + bell-curve mapping)
5. Executive synthesis: Top 3-4 demographic concerns and key findings
6. Two-dataset comparative analysis and delta computation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from engine.base import (
    DemographicMeasureResult,
    QualityCheckResult,
    DemographicDataset,
)
from engine.sex_composition import compute_block_a
from engine.age_dependency import compute_block_b
from engine.fertility import compute_block_c
from engine.mortality import compute_block_d
from engine.quality import run_all_quality_checks
from engine.interpretation import interpret_measure, BENCHMARK_REGISTRY


@dataclass
class DemographicPipelineResult:
    """Full execution output container for the Vital Stats Suite."""
    dataset_name: str
    year: Optional[int]
    region: Optional[str]
    quality_checks: Dict[str, QualityCheckResult]
    measures: Dict[str, DemographicMeasureResult]
    top_concerns: List[Dict[str, Any]]
    key_strengths: List[Dict[str, Any]]
    executive_summary: str
    computable_count: int
    total_measures_target: int = 22

    def get_measure(self, code: str) -> Optional[DemographicMeasureResult]:
        return self.measures.get(code)

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "year": self.year,
            "region": self.region,
            "computable_count": self.computable_count,
            "measures": {k: v.to_dict() for k, v in self.measures.items()},
            "quality_checks": {k: v.to_dict() for k, v in self.quality_checks.items()},
            "top_concerns": self.top_concerns,
            "key_strengths": self.key_strengths,
            "executive_summary": self.executive_summary,
        }


@dataclass
class ComparisonResult:
    """Container for two-dataset comparative evaluation."""
    dataset_a_name: str
    dataset_b_name: str
    result_a: DemographicPipelineResult
    result_b: DemographicPipelineResult
    comparison_table: pd.DataFrame
    narrative_summary: str
    key_divergences: List[Dict[str, Any]]


def generate_executive_summary(
    measures: Dict[str, DemographicMeasureResult],
    quality_checks: Dict[str, QualityCheckResult],
    dataset_name: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:
    """Generates the top 3-4 demographic concerns and executive plain-language summary."""
    concerns: List[Dict[str, Any]] = []
    strengths: List[Dict[str, Any]] = []
    
    # Check data quality first
    whipple = quality_checks.get("WHIPPLE")
    if whipple and whipple.status in ("WARNING", "SEVERE"):
        concerns.append({
            "title": f"Data Quality Alert: Age Heaping (Whipple's Index {whipple.score:.1f})",
            "measure": "WHIPPLE",
            "severity": whipple.status,
            "description": whipple.interpretation,
            "recommendation": whipple.recommendation,
        })
        
    pec = quality_checks.get("PEC")
    if pec and pec.status in ("WARNING", "SEVERE"):
        concerns.append({
            "title": f"Census Coverage Omission ({pec.score:.1f}% Undercount)",
            "measure": "PEC",
            "severity": pec.status,
            "description": pec.interpretation,
            "recommendation": pec.recommendation,
        })
        
    # Check demographic measures
    for code, res in measures.items():
        interp = res.interpretation or {}
        st = interp.get("status", "")
        if st in ("CRITICAL", "CONCERNING"):
            concerns.append({
                "title": f"{res.name}: {res.formatted_value}",
                "measure": code,
                "severity": st,
                "description": interp.get("label", ""),
                "recommendation": res.notes or "",
            })
        elif st in ("EXCELLENT", "GOOD"):
            strengths.append({
                "title": f"{res.name}: {res.formatted_value}",
                "measure": code,
                "severity": st,
                "description": interp.get("label", ""),
            })
            
    # Sort concerns by severity
    severity_order = {"CRITICAL": 0, "SEVERE": 1, "CONCERNING": 2, "WARNING": 3, "MODERATE": 4, "GOOD": 5, "EXCELLENT": 6}
    concerns.sort(key=lambda x: severity_order.get(x["severity"], 10))
    top_3_4_concerns = concerns[:4]
    
    # Construct Plain-Language Narrative
    tfr = measures.get("TFR")
    imr = measures.get("IMR")
    tdr = measures.get("TDR")
    oadr = measures.get("OADR")
    sr = measures.get("SR")
    
    parts = [f"Analysis of **{dataset_name}** covers {len(measures)} evaluated demographic indicators."]
    
    if tfr:
        if tfr.raw_value < 1.5:
            parts.append(f"Fertility is at critically low sub-replacement levels (TFR {tfr.raw_value:.2f}), accelerating demographic aging.")
        elif tfr.raw_value < 2.1:
            parts.append(f"Fertility is below replacement level (TFR {tfr.raw_value:.2f}), signaling a stabilizing to contracting population trajectory.")
        elif tfr.raw_value <= 2.5:
            parts.append(f"Fertility is near ideal demographic replacement (TFR {tfr.raw_value:.2f}).")
        else:
            parts.append(f"Fertility remains high (TFR {tfr.raw_value:.2f}), maintaining youthful population momentum.")
            
    if imr:
        if imr.raw_value <= 12.0:
            parts.append(f"Infant survival is strong (IMR {imr.raw_value:.1f} per 1,000 live births), meeting international SDG targets.")
        else:
            parts.append(f"Infant mortality remains elevated at {imr.raw_value:.1f} per 1,000 live births, requiring continued maternal and neonatal intervention.")
            
    if tdr and oadr:
        parts.append(f"The dependency ratio is {tdr.raw_value:.1f} per 100 workers, with elderly dependency at {oadr.raw_value:.1f}.")
        
    if sr and abs(sr.raw_value - 100.0) > 6.0:
        parts.append(f"Sex ratio shows notable skew ({sr.raw_value:.1f} males per 100 females).")
        
    summary_text = " ".join(parts)
    return top_3_4_concerns, strengths, summary_text


def run_demographic_pipeline(dataset: DemographicDataset) -> DemographicPipelineResult:
    """
    Executes the end-to-end demographic processing pipeline on a dataset.
    """
    # 1. Quality checks
    quality_checks = run_all_quality_checks(dataset)
    
    # 2. Block computations
    measures: Dict[str, DemographicMeasureResult] = {}
    measures.update(compute_block_a(dataset))
    measures.update(compute_block_b(dataset))
    measures.update(compute_block_c(dataset))
    measures.update(compute_block_d(dataset))
    
    # 3. Interpretation pass
    for code, m in measures.items():
        interpret_measure(m)
        
    # 4. Synthesize top concerns & plain-language summary
    concerns, strengths, summary = generate_executive_summary(measures, quality_checks, dataset.name)
    
    return DemographicPipelineResult(
        dataset_name=dataset.name,
        year=dataset.year,
        region=dataset.region,
        quality_checks=quality_checks,
        measures=measures,
        top_concerns=concerns,
        key_strengths=strengths,
        executive_summary=summary,
        computable_count=len(measures),
        total_measures_target=22,
    )


def compare_two_datasets(
    dataset_a: DemographicDataset,
    dataset_b: DemographicDataset,
) -> ComparisonResult:
    """
    Executes full pipeline on both datasets and computes side-by-side comparative diffs.
    """
    res_a = run_demographic_pipeline(dataset_a)
    res_b = run_demographic_pipeline(dataset_b)
    
    all_codes = sorted(list(set(res_a.measures.keys()) | set(res_b.measures.keys())))
    
    rows = []
    divergences = []
    
    for code in all_codes:
        m_a = res_a.measures.get(code)
        m_b = res_b.measures.get(code)
        name = m_a.name if m_a else (m_b.name if m_b else code)
        block = m_a.block if m_a else (m_b.block if m_b else "General")
        unit = m_a.unit if m_a else (m_b.unit if m_b else "")
        
        val_a = m_a.raw_value if m_a else None
        val_b = m_b.raw_value if m_b else None
        
        if val_a is not None and val_b is not None:
            delta = val_b - val_a
            pct_change = (delta / abs(val_a) * 100.0) if val_a != 0 else 0.0
            fmt_a = m_a.formatted_value
            fmt_b = m_b.formatted_value
            status_a = m_a.interpretation.get("status") if m_a.interpretation else "-"
            status_b = m_b.interpretation.get("status") if m_b.interpretation else "-"
            
            if abs(pct_change) >= 15.0 or (status_a != status_b):
                divergences.append({
                    "code": code,
                    "name": name,
                    "val_a": val_a,
                    "val_b": val_b,
                    "delta": delta,
                    "pct_change": pct_change,
                    "status_a": status_a,
                    "status_b": status_b,
                })
        else:
            delta = None
            pct_change = None
            fmt_a = m_a.formatted_value if m_a else "N/A"
            fmt_b = m_b.formatted_value if m_b else "N/A"
            status_a = "-"
            status_b = "-"
            
        rows.append({
            "Block": block,
            "Measure Code": code,
            "Measure Name": name,
            f"{dataset_a.name}": fmt_a,
            f"{dataset_b.name}": fmt_b,
            "Absolute Delta": f"{delta:+.2f} {unit}" if delta is not None else "N/A",
            "Percentage Change": f"{pct_change:+.1f}%" if pct_change is not None else "N/A",
            f"Status ({dataset_a.name})": status_a,
            f"Status ({dataset_b.name})": status_b,
        })
        
    comp_df = pd.DataFrame(rows)
    
    # Comparative Narrative
    narrative_lines = [
        f"Comparative demographic evaluation between **{dataset_a.name}** and **{dataset_b.name}** identifies {len(divergences)} significant shifts (>= 15% change or status transition)."
    ]
    for d in divergences[:3]:
        arrow = "increased" if d["delta"] > 0 else "declined"
        narrative_lines.append(
            f"• **{d['name']}** {arrow} by {abs(d['pct_change']):.1f}% (from {d['val_a']:.2f} to {d['val_b']:.2f})."
        )
        
    return ComparisonResult(
        dataset_a_name=dataset_a.name,
        dataset_b_name=dataset_b.name,
        result_a=res_a,
        result_b=res_b,
        comparison_table=comp_df,
        narrative_summary="\n".join(narrative_lines),
        key_divergences=divergences,
    )
