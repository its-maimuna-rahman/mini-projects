"""
Vital Stats Suite — Demographic Intelligence & Policy Engine
Implements:
- Universal CSV & JSON demographic ingestion & smart age-distribution aggregator
- Two-Dataset Comparison Mode (support comparing 2 uploaded CSVs / JSONs / benchmarks)
- Full battery of 22 demographic measures across 4 core blocks
- Demographic data quality audits (Whipple, Myers, PEC)
- Interactive comparative population pyramids, age composition, vital schedules, and calm bell-curve gauges
- Module 2: Long-term trajectory simulation & prescriptive policy engine
- Multi-format exports (Detailed PDF, Executive Brief PDF, Standalone HTML)
- High-contrast, crystal-clear editorial UI design system with rounded corners
"""

from __future__ import annotations
import os
import sys
import json
import io
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Direct Python launcher hook: if run via `python3 app.py`, boot Streamlit runner
if __name__ == "__main__" and not st.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", str(Path(__file__).resolve())] + sys.argv[1:]
    sys.exit(stcli.main())

BASE_DIR = Path(__file__).resolve().parent

from engine.base import DemographicDataset
from engine.pipeline import run_demographic_pipeline, compare_two_datasets
from engine.quality import validate_dataset_completeness
from engine.missing_assistant import explain_missing_gap
from engine.inference import simulate_demographic_trajectory
from engine.loader import (
    load_demographic_dataset,
    generate_sample_age_distribution_csv,
    generate_sample_summary_csv,
)
from reports.pdf_export import generate_detailed_pdf_report, generate_summary_pdf_brief
from reports.html_export import generate_standalone_html_dashboard
from ui.components import (
    create_population_pyramid,
    create_age_composition_donut,
    create_digit_preference_chart,
    create_fertility_schedule_chart,
    create_mortality_schedule_chart,
    create_trajectory_chart,
    render_calm_gauge,
    PALETTE,
)


# ---------------------------------------------------------
# Page Configuration & High-Contrast Editorial Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vital Stats Suite",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,500&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Clean typography & high-contrast editorial base */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'Newsreader', Georgia, serif !important;
        color: #1F1B16 !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em;
    }
    h1 {
        font-size: 2.15rem !important;
        margin-bottom: 0.25rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
        margin-top: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    h3 {
        font-size: 1.15rem !important;
        margin-top: 0.6rem !important;
        margin-bottom: 0.3rem !important;
    }

    /* Rounded Cards & Containers */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 3px rgba(31, 27, 22, 0.03) !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif !important;
        font-variant-numeric: tabular-nums !important;
        font-weight: 700 !important;
        color: #1F1B16 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #5A5248 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }

    /* Buttons with smooth rounded corners */
    .stButton>button, .stDownloadButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        transition: all 0.18s ease-in-out !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Newsreader', Georgia, serif !important;
        font-size: 1.1rem !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(31, 27, 22, 0.03) !important;
    }

    /* Subtle rounded tables & plots */
    .stPlotlyChart {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
</style>
"""
st.html(CUSTOM_CSS)


# ---------------------------------------------------------
# Sidebar Controls: Universal Dataset Loading & Comparison
# ---------------------------------------------------------
with st.sidebar:
    st.title("Vital Stats Suite")
    st.caption("Editorial demographic laboratory for vital statistics diagnostics, 22 standard demographic measures, two-dataset comparative audits, and long-term policy forecasting.")
    
    st.divider()
    st.subheader("1. Primary Dataset")
    
    dataset_source_type = st.segmented_control(
        "Primary Dataset Source",
        ["Built-in Benchmark", "Upload CSV / JSON"],
        default="Built-in Benchmark",
        label_visibility="collapsed",
    )
    
    primary_ds: Optional[DemographicDataset] = None
    
    if dataset_source_type == "Built-in Benchmark":
        benchmark_choice = st.selectbox(
            "Select Benchmark Dataset",
            [
                "National Census 2011 (Baseline)",
                "National Census 2022 (Modern Transition)",
                "Historical Dirty Census (High Heaping / Gaps)",
            ]
        )
        if benchmark_choice == "National Census 2011 (Baseline)":
            primary_ds = load_demographic_dataset(BASE_DIR / "sample_data" / "census_2011.json", name="National Census 2011 (Baseline)")
        elif benchmark_choice == "National Census 2022 (Modern Transition)":
            primary_ds = load_demographic_dataset(BASE_DIR / "sample_data" / "census_2022.json", name="National Census 2022 (Modern Transition)")
        else:
            primary_ds = load_demographic_dataset(BASE_DIR / "sample_data" / "dirty_census.json", name="Historical Dirty Census (Gaps & Heaping)")
    else:
        uploaded_primary = st.file_uploader(
            "Upload Primary Demographic File (.csv or .json)",
            type=["csv", "json"],
            key="primary_file_uploader",
            help="Upload an Age-Sex distribution CSV (columns: age/age_group, male, female, total, deaths, births) or indicators CSV / JSON."
        )
        if uploaded_primary is not None:
            custom_name = st.text_input("Dataset Label (Optional)", value=uploaded_primary.name.rsplit(".", 1)[0], key="primary_name")
            primary_ds = load_demographic_dataset(uploaded_primary, name=custom_name)
        else:
            st.info("Upload a CSV or JSON file to analyze.", icon=":material/upload_file:")
            
    st.divider()
    enable_comparison = st.toggle("Enable Two-Dataset Comparison", value=False)
    compare_ds: Optional[DemographicDataset] = None
    
    if enable_comparison:
        st.subheader("2. Comparison Dataset (Dataset B)")
        comp_source_type = st.segmented_control(
            "Comparison Source",
            ["Built-in Benchmark", "Upload Second CSV / JSON"],
            default="Built-in Benchmark",
            key="comp_source_type_seg"
        )
        
        if comp_source_type == "Built-in Benchmark":
            comp_benchmark_choice = st.selectbox(
                "Select Benchmark to Compare Against",
                [
                    "National Census 2011 (Baseline)",
                    "National Census 2022 (Modern Transition)",
                    "Historical Dirty Census (High Heaping / Gaps)",
                ],
                index=1 if dataset_source_type == "Built-in Benchmark" and benchmark_choice == "National Census 2011 (Baseline)" else 0
            )
            if comp_benchmark_choice == "National Census 2011 (Baseline)":
                compare_ds = load_demographic_dataset(BASE_DIR / "sample_data" / "census_2011.json", name="National Census 2011 (Baseline)")
            elif comp_benchmark_choice == "National Census 2022 (Modern Transition)":
                compare_ds = load_demographic_dataset(BASE_DIR / "sample_data" / "census_2022.json", name="National Census 2022 (Modern Transition)")
            else:
                compare_ds = load_demographic_dataset(BASE_DIR / "sample_data" / "dirty_census.json", name="Historical Dirty Census (Gaps & Heaping)")
        else:
            uploaded_comp = st.file_uploader(
                "Upload Comparison Demographic File (.csv or .json)",
                type=["csv", "json"],
                key="comp_file_uploader",
                help="Upload a second dataset to perform side-by-side comparative analysis."
            )
            if uploaded_comp is not None:
                comp_custom_name = st.text_input("Comparison Label (Optional)", value=uploaded_comp.name.rsplit(".", 1)[0], key="comp_name")
                compare_ds = load_demographic_dataset(uploaded_comp, name=comp_custom_name)
            else:
                st.warning("Please upload a comparison file or choose a benchmark.")
                
    st.divider()
    with st.expander("Download Sample CSV Templates", icon=":material/download:"):
        st.caption("Download clean CSV templates to populate with your own demographic data:")
        sample_age_csv = generate_sample_age_distribution_csv()
        st.download_button(
            "Sample Age-Sex Table (CSV)",
            data=sample_age_csv,
            file_name="sample_demographic_age_table.csv",
            mime="text/csv",
            icon=":material/table_chart:",
        )
        sample_sum_csv = generate_sample_summary_csv()
        st.download_button(
            "Sample Indicators Table (CSV)",
            data=sample_sum_csv,
            file_name="sample_demographic_indicators.csv",
            mime="text/csv",
            icon=":material/query_stats:",
        )
        
    with st.expander("Demographer Assistant Settings", icon=":material/settings:"):
        gemini_key = st.text_input("Gemini API Key (Optional)", type="password", help="Enables live generative demographer explanations for missing columns.")


# Stop execution early if primary dataset is not yet loaded
if primary_ds is None:
    st.title("Vital Stats Suite")
    st.info("Please select a benchmark dataset or upload your primary demographic CSV/JSON file in the sidebar to begin.", icon=":material/arrow_back:")
    st.stop()


# ---------------------------------------------------------
# Main Application Content & Navigation Tabs
# ---------------------------------------------------------
tab_module1, tab_module2, tab_reference = st.tabs([
    "Module 1: Vital Statistics Suite",
    "Module 2: Inference & Policy Engine",
    "Reference Manual & Benchmarks",
])


# =========================================================
# TAB 1: MODULE 1 — VITAL STATISTICS SUITE
# =========================================================
with tab_module1:
    pipeline_res = run_demographic_pipeline(primary_ds)
    
    # Header Bar
    title_col, badge_col = st.columns([3, 1])
    with title_col:
        st.title(primary_ds.name)
    with badge_col:
        if enable_comparison and compare_ds:
            st.badge(f"Comparing with: {compare_ds.name}", icon=":material/compare_arrows:", color="blue")
            
    # Key Demographic Metrics Ribbon
    with st.container(horizontal=True):
        st.metric("Total Population", f"{primary_ds.total_population:,.0f}" if primary_ds.total_population else "N/A", border=True)
        st.metric("Census Year", f"{primary_ds.year}" if primary_ds.year else "Baseline", border=True)
        st.metric("Geographic Scope", f"{primary_ds.region or 'National'}", border=True)
        st.metric("Evaluated Battery", f"{pipeline_res.computable_count} / {pipeline_res.total_measures_target} Measures", border=True)
        
    # Executive Summary Box
    with st.container(border=True):
        st.subheader(":material/insights: Executive Demographic Synthesis")
        st.write(pipeline_res.executive_summary)
        
    # Priority Demographic Alerts Grid
    if pipeline_res.top_concerns:
        st.subheader("Top Priority Concerns & Statistical Alerts")
        c_cols = st.columns(min(len(pipeline_res.top_concerns), 3))
        for idx, c in enumerate(pipeline_res.top_concerns[:3]):
            with c_cols[idx]:
                with st.container(border=True):
                    sev = c.get("severity", "WARNING")
                    if sev in ("CRITICAL", "SEVERE"):
                        st.badge(f"{sev} Alert", icon=":material/error:", color="red")
                    elif sev in ("CONCERNING", "WARNING"):
                        st.badge(f"{sev} Alert", icon=":material/warning:", color="orange")
                    else:
                        st.badge(f"{sev} Status", icon=":material/info:", color="blue")
                    st.markdown(f"**{c.get('title')}**")
                    st.caption(c.get("description", ""))
                    if c.get("recommendation"):
                        st.markdown(f"*{c.get('recommendation')}*")
                        
    # Missing Data Assistant Banner
    computable_codes, missing_codes, gaps = validate_dataset_completeness(primary_ds)
    if missing_codes:
        with st.expander(f"Data Gaps Detected ({len(missing_codes)} measures uncomputable) — Demographer Guidance", expanded=False, icon=":material/warning:"):
            st.caption("The following fields were not found in your uploaded dataset. Demographer guidance explains how to supply or reconstruct them:")
            for gap_key, gap_info in gaps.items():
                explanation = explain_missing_gap(gap_key, api_key=gemini_key if 'gemini_key' in locals() else None)
                with st.container(border=True):
                    st.markdown(f"**{explanation['title']}**")
                    st.write(explanation['explanation'])
                    
    # 1. Data Quality Diagnostics
    st.subheader("1. Data Quality & Census Coverage Audits")
    q_col1, q_col2, q_col3 = st.columns(3)
    
    whipple = pipeline_res.quality_checks.get("WHIPPLE")
    myers = pipeline_res.quality_checks.get("MYERS")
    pec = pipeline_res.quality_checks.get("PEC")
    
    with q_col1:
        with st.container(border=True):
            w_score = f"{whipple.score:.2f}" if whipple and whipple.score is not None else "N/A"
            st.metric("Whipple's Index (0 & 5 Heaping)", w_score)
            if whipple and whipple.score is not None:
                if whipple.status == "EXCELLENT":
                    st.badge(f"Status: {whipple.status.title()}", icon=":material/check_circle:", color="green")
                elif whipple.status in ("ACCEPTABLE", "GOOD"):
                    st.badge(f"Status: {whipple.status.title()}", icon=":material/check:", color="blue")
                else:
                    st.badge(f"Status: {whipple.status.title()}", icon=":material/warning:", color="orange")
                st.caption(whipple.interpretation)
            else:
                st.caption("Requires single-year age table (ages 23–62).")
                
    with q_col2:
        with st.container(border=True):
            m_score = f"{myers.score:.2f}" if myers and myers.score is not None else "N/A"
            st.metric("Myers' Blended Index (All Digits 0–9)", m_score)
            if myers and myers.score is not None:
                if myers.status == "EXCELLENT":
                    st.badge(f"Status: {myers.status.title()}", icon=":material/check_circle:", color="green")
                elif myers.status in ("ACCEPTABLE", "GOOD"):
                    st.badge(f"Status: {myers.status.title()}", icon=":material/check:", color="blue")
                else:
                    st.badge(f"Status: {myers.status.title()}", icon=":material/warning:", color="orange")
                st.caption(myers.interpretation)
            else:
                st.caption("Requires single-year age table (ages 10–69).")
                
    with q_col3:
        with st.container(border=True):
            pec_score = f"{pec.score:.2f}%" if pec and pec.score is not None else "N/A"
            st.metric("PEC Net Undercount Rate", pec_score)
            if pec and pec.score is not None:
                if pec.status == "EXCELLENT":
                    st.badge(f"Status: {pec.status.title()}", icon=":material/check_circle:", color="green")
                elif pec.status in ("ACCEPTABLE", "GOOD"):
                    st.badge(f"Status: {pec.status.title()}", icon=":material/check:", color="blue")
                else:
                    st.badge(f"Status: {pec.status.title()}", icon=":material/warning:", color="orange")
                st.caption(pec.interpretation)
            else:
                st.caption("PEC coverage rate or omission percentage not specified.")
                
    # 2. Interactive Visualization Laboratory
    st.subheader("2. Interactive Demographic Visualizations")
    
    v_tab1, v_tab2, v_tab3, v_tab4 = st.tabs([
        "Population Pyramid",
        "Age Composition Breakdown",
        "Digit Preference Audit (0–9)",
        "Vital Schedules (ASFR & ASDR)",
    ])
    
    pyr_df = primary_ds.age_group_5yr if primary_ds.age_group_5yr is not None else primary_ds.single_year_ages
    
    with v_tab1:
        if pyr_df is not None and not pyr_df.empty:
            ctrl_c1, ctrl_c2 = st.columns([1, 2])
            with ctrl_c1:
                pyr_mode = st.segmented_control("Display Metric", ["Percentage (%)", "Population Counts"], default="Percentage (%)")
            
            comp_pyr_df = None
            if enable_comparison and compare_ds is not None:
                comp_pyr_df = compare_ds.age_group_5yr if compare_ds.age_group_5yr is not None else compare_ds.single_year_ages
                
            fig_pyr = create_population_pyramid(
                df_single_or_5yr=pyr_df,
                title=f"Population Structure: {primary_ds.name}" + (f" vs {compare_ds.name}" if comp_pyr_df is not None else ""),
                df_compare=comp_pyr_df,
                current_label=str(primary_ds.year or primary_ds.name),
                compare_label=str(compare_ds.year or compare_ds.name) if compare_ds else None,
                as_percentage=(pyr_mode == "Percentage (%)"),
            )
            st.plotly_chart(fig_pyr)
        else:
            st.info("Single-year or 5-year age table not provided for pyramid visualization.", icon=":material/info:")
            
    with v_tab2:
        p_0_14 = primary_ds.pop_0_14
        p_15_64 = primary_ds.pop_15_64
        p_65_plus = primary_ds.pop_65_plus
        
        if p_0_14 is not None and p_15_64 is not None and p_65_plus is not None:
            ac_col1, ac_col2 = st.columns([1.2, 1])
            with ac_col1:
                fig_donut = create_age_composition_donut(p_0_14, p_15_64, p_65_plus)
                st.plotly_chart(fig_donut)
            with ac_col2:
                with st.container(border=True):
                    st.subheader("Functional Demographic Segments")
                    tot_func = p_0_14 + p_15_64 + p_65_plus
                    st.write(f"• **Youth Cohort (0–14):** {p_0_14:,.0f} ({(p_0_14/tot_func)*100:.1f}%)")
                    st.write(f"• **Productive Workforce (15–64):** {p_15_64:,.0f} ({(p_15_64/tot_func)*100:.1f}%)")
                    st.write(f"• **Elderly Persons (65+):** {p_65_plus:,.0f} ({(p_65_plus/tot_func)*100:.1f}%)")
                    
                    tdr_val = ((p_0_14 + p_65_plus) / p_15_64) * 100.0 if p_15_64 > 0 else 0.0
                    st.divider()
                    st.metric("Total Dependency Ratio (TDR)", f"{tdr_val:.1f}", help="Dependents per 100 working-age individuals.")
        else:
            st.info("Broad age categories (0-14, 15-64, 65+) not provided in current dataset.", icon=":material/info:")
            
    with v_tab3:
        if primary_ds.single_year_ages is not None and not primary_ds.single_year_ages.empty:
            fig_myers = create_digit_preference_chart(primary_ds.single_year_ages)
            st.plotly_chart(fig_myers)
            if myers and myers.details:
                pref_d = myers.details.get("most_preferred_digit")
                avoid_d = myers.details.get("most_avoided_digit")
                st.caption(f"Myers Diagnostic: Peak preferred digit is **'{pref_d}'**; most avoided digit is **'{avoid_d}'**.")
        else:
            st.info("Myers terminal digit preference analysis requires single-year age table (0-90+).", icon=":material/info:")
            
    with v_tab4:
        sched_col1, sched_col2 = st.columns(2)
        with sched_col1:
            if primary_ds.fertility_schedule is not None and not primary_ds.fertility_schedule.empty:
                fig_asfr = create_fertility_schedule_chart(primary_ds.fertility_schedule)
                st.plotly_chart(fig_asfr)
            else:
                st.info("Maternal age-specific fertility schedule not provided.", icon=":material/info:")
                
        with sched_col2:
            if primary_ds.mortality_schedule is not None and not primary_ds.mortality_schedule.empty:
                log_choice = st.toggle("Logarithmic Mortality Scale", value=False)
                fig_asdr = create_mortality_schedule_chart(primary_ds.mortality_schedule, log_scale=log_choice)
                st.plotly_chart(fig_asdr)
            else:
                st.info("Age-specific mortality schedule not provided.", icon=":material/info:")

    # 3. Two-Dataset Comparison Section (if activated)
    if enable_comparison and compare_ds is not None:
        st.subheader(":material/compare_arrows: Comparative Evaluation & Divergence Audit")
        comp_result = compare_two_datasets(primary_ds, compare_ds)
        
        with st.container(border=True):
            st.markdown("#### Comparative Synthesis")
            st.write(comp_result.narrative_summary)
            
        st.dataframe(
            comp_result.comparison_table,
            hide_index=True,
        )

    # 4. Full Battery of 22 Demographic Measures & Calm Gauges
    st.subheader("3. Full Battery of 22 Demographic Measures")
    
    m_tab_a, m_tab_b, m_tab_c, m_tab_d = st.tabs([
        "Block A: Sex Composition (3)",
        "Block B: Age & Dependency (4)",
        "Block C: Fertility (7)",
        "Block D: Mortality & Standardization (8)",
    ])
    
    def render_block_measures(codes: List[str]):
        for code in codes:
            m = pipeline_res.measures.get(code)
            if m:
                interp = m.interpretation or {}
                render_calm_gauge(
                    measure_name=m.name,
                    value=m.raw_value,
                    formatted_value=m.formatted_value,
                    unit=m.unit,
                    status=interp.get("status", "MODERATE"),
                    status_label=interp.get("label", "Standard"),
                    gauge_min=interp.get("gauge_min", 0.0),
                    gauge_max=interp.get("gauge_max", 100.0),
                    source=interp.get("source", "Demographic Standard"),
                    is_heuristic=interp.get("is_heuristic", False),
                )
                with st.expander(f"Formula & Academic Citation: {m.name} ({m.code})", icon=":material/menu_book:"):
                    st.markdown(f"**Mathematical Formula:** `{m.formula}`")
                    st.markdown(f"**Citation:** *{m.citation}*")
                    if m.notes:
                        st.markdown(f"**Demographic Context:** {m.notes}")
            else:
                with st.container(border=True):
                    st.markdown(f":material/info: **{code} — Not Computable** *(Required input data missing from source dataset)*")
                    
    with m_tab_a:
        render_block_measures(["MP", "SR", "EXCESS_M"])
    with m_tab_b:
        render_block_measures(["ACR", "TDR", "CDR_CHILD", "OADR"])
    with m_tab_c:
        render_block_measures(["CBR", "MBR", "GFR", "ASFR", "TFR", "GRR", "NRR"])
    with m_tab_d:
        render_block_measures(["CDR", "CORRECTED_CDR", "NMR", "IMR", "CMR", "ASDR", "DSDR", "SMR", "ISDR"])

    # 5. Export & Dissemination Center
    st.subheader(":material/file_download: 4. Export & Dissemination Center")
    
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    
    with exp_col1:
        with st.container(border=True):
            st.markdown("#### Detailed PDF Report")
            st.caption("Complete statistical report covering all 22 measures, formulas, and citations.")
            pdf_detailed_bytes = generate_detailed_pdf_report(pipeline_res)
            st.download_button(
                label="Download Detailed PDF",
                data=pdf_detailed_bytes,
                file_name=f"Demographic_Report_{primary_ds.name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                icon=":material/description:",
            )
            
    with exp_col2:
        with st.container(border=True):
            st.markdown("#### Executive Summary PDF")
            st.caption("1-page executive brief featuring top policy concerns and key findings.")
            pdf_summary_bytes = generate_summary_pdf_brief(pipeline_res)
            st.download_button(
                label="Download Summary Brief",
                data=pdf_summary_bytes,
                file_name=f"Executive_Brief_{primary_ds.name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                icon=":material/article:",
            )
            
    with exp_col3:
        with st.container(border=True):
            st.markdown("#### Standalone HTML")
            st.caption("Self-contained interactive dashboard for offline dissemination.")
            html_dashboard_str = generate_standalone_html_dashboard(pipeline_res)
            st.download_button(
                label="Download HTML Dashboard",
                data=html_dashboard_str,
                file_name=f"Dashboard_{primary_ds.name.replace(' ', '_')}.html",
                mime="text/html",
                icon=":material/html:",
            )


# =========================================================
# TAB 2: MODULE 2 — INFERENCE & POLICY ENGINE
# =========================================================
with tab_module2:
    st.title("Module 2: Inference & Policy Engine")
    st.caption("Historical Time-Series Ingestion &bull; Trajectory Simulation &bull; Prescriptive Policy Output")
    
    df_ts = pd.read_csv(BASE_DIR / "sample_data" / "time_series_1970_2024.csv")
    
    with st.container(border=True):
        st.subheader(":material/tune: Simulation Parameters")
        p_col1, p_col2 = st.columns([1, 1])
        with p_col1:
            proj_horizon = st.slider("Projection Horizon (Years)", min_value=10, max_value=50, value=30, step=5)
        with p_col2:
            fert_scenario = st.segmented_control(
                "Fertility Scenario Variant",
                ["medium", "low", "high"],
                default="medium",
                format_func=lambda x: f"{x.title()} Variant",
            )
            
    proj_result = simulate_demographic_trajectory(
        historical_df=df_ts,
        projection_horizon_years=proj_horizon,
        fertility_scenario=fert_scenario or "medium",
    )
    
    with st.container(border=True):
        st.subheader(":material/insights: Demographic Trajectory & Policy Outlook")
        st.write(proj_result.narrative_policy_brief)
        
    fig_traj = create_trajectory_chart(
        combined_df=proj_result.combined_df,
        dividend_start_year=proj_result.dividend_start_year,
        dividend_end_year=proj_result.dividend_end_year,
    )
    st.plotly_chart(fig_traj)
    
    with st.expander("Model Assumptions & Mathematical Specifications", icon=":material/functions:"):
        for assump in proj_result.assumptions_summary:
            st.markdown(f"• {assump}")
            
    st.subheader(":material/policy: Prescriptive Policy Recommendations")
    st.caption("Targeted interventions mapped directly to projected threshold inflections:")
    
    for flag in proj_result.policy_flags:
        with st.container(border=True):
            f_col1, f_col2 = st.columns([4, 1])
            with f_col1:
                st.markdown(f"### {flag.title}")
            with f_col2:
                if flag.severity in ("CRITICAL", "SEVERE"):
                    st.badge(f"{flag.severity}", icon=":material/error:", color="red")
                elif flag.severity in ("CONCERNING", "WARNING"):
                    st.badge(f"{flag.severity}", icon=":material/warning:", color="orange")
                else:
                    st.badge(f"{flag.severity}", icon=":material/info:", color="blue")
                    
            st.write(flag.description)
            st.caption(f"**Demographic Rationale:** {flag.rationale}")
            st.markdown("**Recommended Policy Interventions:**")
            for rec in flag.policy_recommendations:
                st.markdown(f"• {rec}")


# =========================================================
# TAB 3: REFERENCE & BENCHMARK MANUAL
# =========================================================
with tab_reference:
    st.title("Demographic Reference Manual & UN/WHO Standards")
    st.caption(
        "The Vital Stats Suite adheres to international statistical standards from the United Nations DESA Population Division, "
        "World Health Organization (WHO), and standard demographic texts (Preston et al. 2001; Shryock & Siegel 1976; Bhende & Kanitkar 2010)."
    )
    
    with open(BASE_DIR / "ENGINE.md", "r", encoding="utf-8") as f:
        engine_doc = f.read()
    st.markdown(engine_doc)
