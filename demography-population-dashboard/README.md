# Vital Stats Suite — Operating & Architecture Guide

A professional demographic intelligence suite and policy engine designed to ingest raw census or vital registration data, execute rigorous data-quality audits (Whipple's Index, Myers' Index, PEC coverage), compute a full battery of **22 demographic measures**, evaluate findings against international benchmarks (UN/WHO/CDC), simulate future population trajectories, and formulate prescriptive policy recommendations.

---

## 🏛️ System Architecture

```
demeow/
├── app.py                      # Main Streamlit dashboard application
├── ENGINE.md                   # Authoritative mathematical formula & citation manual
├── README.md                   # User and operating guide
├── engine/                     # Core demographic calculation engine
│   ├── __init__.py             # Public engine API
│   ├── base.py                 # Core data models, dataclasses & standard populations
│   ├── sex_composition.py      # Block A: Sex composition (MP, SR, Excess of Males)
│   ├── age_dependency.py       # Block B: Age & dependency (ACR, TDR, CDR_child, OADR)
│   ├── fertility.py            # Block C: Fertility (CBR, MBR, GFR, ASFR, TFR, GRR, NRR)
│   ├── mortality.py            # Block D: Mortality & standardization (CDR, NMR, IMR, CMR, ASDR, DSDR, SMR, ISDR)
│   ├── quality.py              # Data quality audits (Whipple, Myers, PEC, Schema validator)
│   ├── interpretation.py       # UN/WHO benchmark registry & calm gauge mapping
│   ├── inference.py            # Module 2: Trajectory simulation & policy recommendation engine
│   ├── missing_assistant.py    # Missing-column assistant (built-in + Gemini API hook)
│   └── pipeline.py             # Pipeline orchestrator & two-dataset comparison engine
├── reports/                    # Multi-format report generators
│   ├── pdf_export.py           # Detailed statistical report & 1-page summary PDF generator
│   └── html_export.py          # Standalone offline HTML dashboard generator
├── ui/                         # Visual components
│   └── components.py           # Population pyramid, calm bell-curve gauges, trajectory charts
├── sample_data/                # Built-in benchmark and test datasets
│   ├── census_2011.json        # Benchmark National Census 2011
│   ├── census_2022.json        # Modern transitioned National Census 2022
│   ├── dirty_census.json       # Synthetic dataset with digit heaping & missing columns
│   ├── time_series_1970_2024.csv # 55-year historical demographic time series
│   └── generate_samples.py     # Sample dataset generator script
└── tests/                      # Automated unit test suite (26 tests)
    ├── conftest.py             # Pytest path configuration
    ├── test_sex_composition.py # Block A unit tests vs textbook examples
    ├── test_age_dependency.py  # Block B unit tests vs standard age structures
    ├── test_fertility.py       # Block C unit tests (ASFR → TFR → GRR → NRR)
    ├── test_mortality.py       # Block D unit tests & direct/indirect reconciliation
    ├── test_quality.py         # Whipple, Myers, and PEC validation tests
    ├── test_pipeline.py        # End-to-end pipeline & comparison tests
    ├── test_inference.py       # Trajectory simulation & policy flag tests
    └── test_exports.py         # PDF and HTML generator tests
```

---

## ⚡ Quickstart & Execution

### 1. Prerequisites & Dependencies
All demographic and dashboard libraries (`streamlit`, `pandas`, `numpy`, `scipy`, `plotly`, `reportlab`, `fpdf2`, `matplotlib`, `jinja2`, `requests`, `pytest`) can be run directly in your system environment or within a virtual environment.

To install/verify system packages without a virtual environment on Ubuntu:
```bash
pip3 install --user streamlit fpdf2 --break-system-packages
```

---

### 2. Running the Application

You can start the dashboard in either of these ways:

#### Option A: Direct Python Execution (No venv needed)
```bash
python3 app.py
```

#### Option B: Standard Streamlit Command
```bash
streamlit run app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

### 3. Run the Automated Unit Tests
```bash
python3 -m pytest tests/
```

---

## 📖 How to Operate the Suite

The interface is structured into three primary tabs:

### Tab 1: Module 1 — Vital Statistics Suite
1. **Choose or Upload a Dataset**:
   - In the sidebar, select one of the built-in reference datasets (*National Census 2011*, *National Census 2022*, or *Historical Dirty Census*) or choose **Upload Custom JSON / CSV**.
2. **Review Data Quality Diagnostics**:
   - **Whipple's Index**: Checks for age heaping / digit preference on terminal digits `0` and `5` across ages 23–62.
   - **Myers' Blended Index**: Evaluates digit attraction across all digits `0` through `9`.
   - **PEC Coverage**: Quantifies net census omission and undercount percentage.
3. **Inspect the Population Pyramid**:
   - Explore the interactive 5-year or single-year age-sex distribution.
4. **Examine the 22 Demographic Measures**:
   - Review each measure categorized into Blocks A, B, C, and D.
   - Each measure features an **editorial calm gauge** showing where the population sits relative to UN/WHO reference bands, along with formula derivations and citations.
5. **Activate Two-Dataset Comparison Mode**:
   - Check **"Enable Two-Dataset Comparison"** in the sidebar and choose a comparison dataset.
   - The dashboard instantly generates side-by-side diff tables, percentage changes, status transitions, and overlaid population pyramids.
6. **Export Findings**:
   - Click **Download Detailed PDF Report** for a complete statistical report.
   - Click **Download Summary Brief (PDF)** for an executive 1-page policy summary.
   - Click **Download Standalone HTML Dashboard** for an interactive, offline-viewable dashboard.

---

### Tab 2: Module 2 — Inference & Policy Engine
1. **Configure Simulation Parameters**:
   - Adjust the **Projection Horizon** (10 to 50 years into the future).
   - Select the **Fertility Scenario**:
     - *Medium Variant*: Gradual convergence towards replacement equilibrium.
     - *Low Variant*: Extended sub-replacement / lowest-low fertility.
     - *High Variant*: Policy-driven fertility rebound.
2. **Analyze the Trajectory Visualization**:
   - Review the demographic dividend window (shaded area where working-age share $\ge 60\%$), total population trajectory, elderly share expansion, and TFR shifts.
3. **Examine Prescriptive Policy Recommendations**:
   - The engine automatically detects threshold crossings (e.g. OADR $> 25$, TFR $< 1.50$, dividend window closure, natural population contraction) and outputs tailored policy interventions for social security, child allowances, eldercare infrastructure, and labor productivity.

---

### Tab 3: Reference Manual & UN/WHO Standards
- Contains the full demographic methodology, mathematical formulas, data quality scales, and academic citations ([ENGINE.md](file:///home/maimuna/Projects/demeow/ENGINE.md)).

---

## 📊 Summary of the 22 Demographic Measures

| Block | Code | Measure Name | Standard Formula | Unit |
|---|---|---|---|---|
| **A. Sex Composition** | `MP` | Masculinity Proportion | $(P_m / P_t) \times 100$ | `%` |
| | `SR` | Sex Ratio | $(P_m / P_f) \times 100$ | `males / 100 females` |
| | `EXCESS_M` | Excess of Males | $P_m - P_f$ | `persons` |
| **B. Age Composition** | `ACR` | Age Composition Ratio | $(P_i / P_t) \times 100$ | `% in broad age groups` |
| | `TDR` | Total Dependency Ratio | $((P_{0-14} + P_{65+}) / P_{15-64}) \times 100$ | `dependents / 100 workers` |
| | `CDR_CHILD` | Child Dependency Ratio | $(P_{0-14} / P_{15-64}) \times 100$ | `children / 100 workers` |
| | `OADR` | Old-Age Dependency Ratio | $(P_{65+} / P_{15-64}) \times 100$ | `elderly / 100 workers` |
| **C. Fertility** | `CBR` | Crude Birth Rate | $(B / P) \times 1,000$ | `births / 1,000 pop` |
| | `MBR` | Marital Birth Rate | $(B_{\text{marital}} / W_{m, 15-49}) \times 1,000$ | `births / 1,000 married women` |
| | `GFR` | General Fertility Rate | $(B / W_{15-49}) \times 1,000$ | `births / 1,000 women 15-49` |
| | `ASFR` | Age-Specific Fertility Rate | $(B_i / W_i) \times 1,000$ | `births / 1,000 in age bracket` |
| | `TFR` | Total Fertility Rate | $5 \times \sum (ASFR_i / 1,000)$ | `children / woman` |
| | `GRR` | Gross Reproduction Rate | $TFR \times (B_f / B_t)$ | `daughters / woman` |
| | `NRR` | Net Reproduction Rate | $\sum (ASFR_{f,i} \times {}_5L_{x_i} / (5 \times l_0))$ | `surviving daughters / woman` |
| **D. Mortality & Standardization** | `CDR` | Crude Death Rate | $(D / P) \times 1,000$ | `deaths / 1,000 pop` |
| | `CORRECTED_CDR` | Corrected Crude Death Rate | $CDR / (1 - \text{Omission Rate})$ | `adjusted deaths / 1,000 pop` |
| | `NMR` | Neonatal Mortality Rate | $(D_{<28\text{d}} / B) \times 1,000$ | `deaths / 1,000 live births` |
| | `IMR` | Infant Mortality Rate | $(D_{<1\text{yr}} / B) \times 1,000$ | `deaths / 1,000 live births` |
| | `CMR` | Child Mortality Rate (U5MR) | $(D_{1-4} / P_{1-4}) \times 1,000$ | `deaths / 1,000 children` |
| | `ASDR` | Age-Specific Death Rate | $(D_i / P_i) \times 1,000$ | `deaths / 1,000 in age bracket` |
| | `DSDR` | Direct Standardized Death Rate | $\sum (ASDR_i \times P^{\text{std}}_i) / \sum P^{\text{std}}_i$ | `standardized deaths / 1,000` |
| | `SMR` | Standardized Mortality Ratio | $D_{\text{obs}} / \sum (P_i \times ASDR^{\text{std}}_i / 1,000)$ | `ratio (Obs / Exp)` |
| | `ISDR` | Indirect Standardized Death Rate| $SMR \times CDR^{\text{std}}$ | `indirect deaths / 1,000` |

---

## 🎨 Design Philosophy ("Claude-pilled" Aesthetic)

- **Palette**:
  - Background: `#F5F1EA` (Warm cream)
  - Text: `#1F1B16` (Near-black)
  - Accent: `#CC785C` (Terracotta)
  - Secondary: `#DDA15E` (Warm sand)
  - Cards: `#FFFFFF` with 1px border `#E5DFD3` (12–16px rounded corners, no heavy drop shadows)
- **Typography**: Editorial serif headings (*Playfair / Georgia / Newsreader*), clean sans body (*Inter*).
- **Calm Gauges**: Horizon indicators designed as tranquil, informative scientific annotations rather than jarring alarm widgets.

---

## 💡 Optional: Enabling Generative LLM Explanations

For live natural-language explanations when input columns are missing:
1. Obtain a Google Gemini API Key.
2. In the sidebar, paste the key into the **"Gemini API Key"** input field, or export it in your shell environment before launching:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   streamlit run app.py
   ```
*(Note: If no API key is provided, the suite automatically falls back to its built-in expert demographic knowledge base).*
