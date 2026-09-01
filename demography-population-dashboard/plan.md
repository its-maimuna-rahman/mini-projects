# Vital Stats Suite — Three-Phase Build Plan (for Google Antigravity)

## 0. Scope recap (from your notes)

**Module 1 — Vital Stats Suite**
One pipeline: upload raw census / vital-registration data → auto data-quality checks (Whipple's Index, age heaping, PEC-style comparison, missing-column detection) → full battery of 22 demographic measures → interpretation layer (good / excellent / bad / v.bad) → population pyramid + dependency/sex-ratio dashboard → two-dataset comparison mode → PDF (detailed) + Summary (top 3–4 concerns) + HTML dashboard export.

**Module 2 — Inference**
Historical data → future trajectory simulation → prescriptive analysis → country's policy output.

**Cross-cutting**
- UI is "Claude-pilled" (see design brief below)
- Missing-column handling needs an LLM assist (your note: "needs many lines of code / gemini mini api") — i.e. when a required column for a measure is absent, a small model call drafts the user-facing message explaining what's missing and why, rather than hand-writing every message.

### The 22 measures, grouped (this grouping drives Phase 1's task split)

| Block | Measures |
|---|---|
| **A. Sex composition** (3) | Masculinity Proportion (MP), Sex Ratio (SR), Excess of Males |
| **B. Age composition & dependency** (4) | Age Composition Ratio (ACR), Total Dependency Ratio (TDR), Child Dependency Ratio (CDR), Old-Age Dependency Ratio (OADR) |
| **C. Fertility** (7) | Crude Birth Rate (CBR), Marital Birth Rate (MBR), General Fertility Rate (GFR), Age-Specific Fertility Rate (ASFR), Total Fertility Rate (TFR), Gross Reproduction Rate (GRR), Net Reproduction Rate (NRR) |
| **D. Mortality & standardization** (8) | Crude Death Rate (CDR), Corrected CDR, Neonatal Mortality Rate (NMR), Infant Mortality Rate (IMR), Child Mortality Rate (CMR), Age-Specific Death Rate (ASDR), Direct Standardized Rate, SMR + Indirect Standardized Rate |

---

## 1. Design brief: "Claude-pilled" UI

Give this paragraph to the frontend agent verbatim so every parallel agent builds to the same system instead of improvising separately:

> Warm, editorial, not "SaaS dashboard." Background `#F5F1EA` (warm cream), primary text near-black `#1F1B16`. Accent `#CC785C` (terracotta) for interactive elements and highlight states — used sparingly, not as a wash of color. Cards are soft white `#FFFFFF` with a 1px hairline border `#E5DFD3`, generously rounded (12–16px), no heavy drop shadows. Typography: a serif for headings (e.g. Tiempos/Georgia-style), clean sans (Inter-style) for body and data. Generous whitespace, single-column reading rhythm even in a dashboard — avoid dense grid-of-widgets BI-tool look. Charts (pyramid, gauges) use the terracotta/cream palette rather than default chart-library rainbow colors. The "high! / normal / within range" gauge you sketched (a bell-curve with a marker) should read like a calm annotation, not an alarm.

---

## 2. Running this in Antigravity

Antigravity's Manager surface lets you spawn several agents in parallel against different workspaces/tasks, each producing a **Task Plan** (step list) and a **Walkthrough** artifact (summary + file diffs + screenshots) you review before merging. Use that structure directly:

- **Phase 1 is backend-only and splits into 4–5 parallel agents** (one per measure block above, plus one for data-quality checks) — they don't touch shared files, so true parallelism is safe.
- **Phase 2 and 3 are mostly single-agent, sequential** — the dashboard and inference layer both depend on Phase 1's engine being merged and correct, so don't parallelize these until the dependency is real (e.g., pyramid viz + PDF export *can* run in parallel once the data layer is stable).
- For every phase, ask the agent to **verify via the browser subagent** once there's a running UI — screenshot the dashboard against the design brief above, not just "tests pass."
- Give each agent textbook worked examples as ground truth (see Phase 1) — for statistical formulas, "runs without error" is not the bar; "matches the known answer" is.

---

## 3. Phase 1 — Core Engine

**Goal:** A tested Python library that takes clean tabular input and returns all 22 measures, correct to known worked examples. No UI yet beyond a CLI/notebook smoke test.

**Antigravity setup:** spawn 5 parallel agents against a shared `engine/` package skeleton (define the interfaces first yourself or in a 0th agent run, so the 5 don't collide):

| Agent | Builds | Verification |
|---|---|---|
| 1. Composition | Block A (MP, SR, Excess of Males) | Unit tests vs. a textbook worked example (e.g. Bhende & Kanitkar-style problem set) |
| 2. Age/Dependency | Block B (ACR, TDR, CDR-child, OADR) | Same — known age-structure dataset with published ratios |
| 3. Fertility | Block C (CBR → NRR) | Known ASFR table → hand-check TFR, GRR, NRR derivations |
| 4. Mortality & Standardization | Block D (CDR-crude → indirect SMR) | Known life-table fragment; direct vs. indirect standardization must agree on a toy population |
| 5. Data Quality | Whipple's Index, age heaping, PEC comparison, missing-column detector | Feed deliberately "dirty" synthetic data (heaped ages, missing column) and assert it's flagged |

**Deliverables:**
- `engine/` package with one function per measure, typed inputs/outputs, docstrings citing the formula
- `engine/quality.py` — validation pass that runs before any measure is computed
- Test suite covering all 22 measures against known values
- A short `ENGINE.md` documenting formula sources (so Phase 2/3 agents don't have to re-derive anything)

**Acceptance criteria (must all pass before Phase 2 starts):**
- [ ] All 22 measures implemented and unit-tested
- [ ] Data-quality module correctly flags heaped ages and missing required columns
- [ ] Direct and indirect standardized rates reconcile on a test dataset
- [ ] No agent's Walkthrough shows unresolved TODOs in the formula logic

---

## 4. Phase 2 — Interpretation & Dashboard

**Goal:** The engine becomes a product — a running dashboard that a non-statistician can read.

**Sequential build order** (each step depends on the last):

1. **Interpretation layer** — a benchmark table mapping each measure to good/excellent/bad/v.bad thresholds (use standard UN/WHO or national benchmark bands where they exist, e.g. IMR bands; note in code where a threshold is a judgment call vs. a sourced standard, since this is the part most likely to get scrutinized).
2. **Missing-column assistant** — when quality checks (Phase 1) flag a gap, call a small model to generate the explanatory message ("X needs column Y because...") instead of hardcoding every message — this is the "gemini mini api" note.
3. **Visualizations** — population pyramid, the gauge/bell-curve "normal vs. high" indicator you sketched, dependency-ratio breakdown. Build against the design brief in §1.
4. **Two-dataset comparison mode** — same engine, run twice, diffed side-by-side (only activates if a second dataset is uploaded).
5. **Dashboard shell** (Streamlit is the fastest path here, matches your note) wiring 1–4 together.
6. **Report export** — PDF (detailed, every measure) and a separate Summary (top 3–4 concerning findings only, plain language) + standalone HTML export of the dashboard.

**Verification:** use Antigravity's browser subagent to actually load the running Streamlit app and screenshot it against the design brief — catch "technically correct but looks like a spreadsheet" early.

**Acceptance criteria:**
- [ ] Every measure has an interpretation label, sourced or explicitly marked as a heuristic
- [ ] Missing-column messages are generated, not hardcoded, and read naturally
- [ ] Pyramid and gauge visuals match the design brief (screenshot-verified)
- [ ] Comparison mode only appears when 2 datasets are present
- [ ] PDF, Summary, and HTML exports all generate without manual steps

---

## 5. Phase 3 — Module 2: Inference & Policy Engine

**Goal:** Given historical time-series data, project forward and surface policy-relevant flags.

1. **Historical data ingestion** — reuse Phase 1's quality checks against a time-indexed dataset.
2. **Trajectory simulation** — start simple and defensible (e.g. linear/logistic extrapolation or basic cohort-component projection) before anything fancier; document the model's assumptions prominently, since projections are the part users will scrutinize most.
3. **Prescriptive analysis** — map projected trajectories against benchmark bands (reuse Phase 2's interpretation layer) to flag which measures are heading in a concerning direction for a given country.
4. **Policy output** — a short, plain-language "what this suggests" panel per flagged measure, feeding off the same summary style as Phase 2's report.
5. **Integration** — Module 2 becomes a second tab/section in the existing dashboard, not a separate app.

**Acceptance criteria:**
- [ ] Simulation model's assumptions are documented in-app, not just in code comments
- [ ] Policy flags are traceable back to a specific projected measure crossing a specific threshold
- [ ] Module 2 is reachable from the Module 1 dashboard, same design system

---

## 6. Suggested first message to Antigravity's Manager surface

```
Project: Vital Stats Suite
Goal: Phase 1 only — core demographic engine, no UI.
Spawn 5 parallel agents against engine/ (interfaces defined in engine/base.py):
  1. Sex composition: MP, SR, Excess of Males
  2. Age/dependency: ACR, TDR, CDR(child), OADR
  3. Fertility: CBR, MBR, GFR, ASFR, TFR, GRR, NRR
  4. Mortality & standardization: CDR(crude), corrected CDR, NMR, IMR, CMR, ASDR,
     direct standardized rate, SMR + indirect standardized rate
  5. Data quality: Whipple's Index, age heaping detection, PEC comparison,
     missing-column detection
Each agent: implement + unit test against a known worked example, report back
via Walkthrough with test results shown, not just "done."
Do not start dashboard work until all 5 are merged and passing.
```

---

## Open questions to confirm before you start

- Confirm the MP / ACR / MBR expansions above match your course material — if they're different terms, the formulas differ and Phase 1's test data changes.
- Is R needed anywhere, or is this Python-only end to end? Your notes mention both near the demography section.
- Do you have (or need to source) actual benchmark bands for the good/excellent/bad/v.bad thresholds, or should Phase 2 start with placeholder bands you refine later?
