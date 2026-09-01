"""
Unit tests for Report Generation (PDF detailed, summary brief, and standalone HTML)
"""

import json
from pathlib import Path
import pytest
import pandas as pd
from engine.base import DemographicDataset
from engine.pipeline import run_demographic_pipeline
from reports.pdf_export import generate_detailed_pdf_report, generate_summary_pdf_brief
from reports.html_export import generate_standalone_html_dashboard


def test_pdf_and_html_generation():
    data_path = Path(__file__).resolve().parent.parent / "sample_data" / "census_2011.json"
    with open(data_path, "r") as f:
        data = json.load(f)
        
    ds = DemographicDataset(
        name=data.get("name"),
        year=data.get("year"),
        total_population=data.get("total_population"),
        male_population=data.get("male_population"),
        female_population=data.get("female_population"),
        pop_0_14=data.get("pop_0_14"),
        pop_15_64=data.get("pop_15_64"),
        pop_65_plus=data.get("pop_65_plus"),
        total_live_births=data.get("total_live_births"),
        total_deaths=data.get("total_deaths"),
        infant_deaths=data.get("infant_deaths"),
        neonatal_deaths=data.get("neonatal_deaths"),
        single_year_ages=pd.DataFrame(data["single_year_ages"]),
        fertility_schedule=pd.DataFrame(data["fertility_schedule"]),
        mortality_schedule=pd.DataFrame(data["mortality_schedule"]),
    )
    
    result = run_demographic_pipeline(ds)
    
    # 1. Detailed PDF
    pdf_detailed = generate_detailed_pdf_report(result)
    assert isinstance(pdf_detailed, bytes)
    assert len(pdf_detailed) > 1000  # Non-empty PDF
    assert pdf_detailed.startswith(b"%PDF")
    
    # 2. Summary PDF Brief
    pdf_summary = generate_summary_pdf_brief(result)
    assert isinstance(pdf_summary, bytes)
    assert len(pdf_summary) > 1000
    assert pdf_summary.startswith(b"%PDF")
    
    # 3. HTML Dashboard
    html_out = generate_standalone_html_dashboard(result)
    assert isinstance(html_out, str)
    assert "Vital Statistics Suite" in html_out
    assert "#F5F1EA" in html_out  # Warm cream palette check
    assert "#CC785C" in html_out  # Terracotta accent check
