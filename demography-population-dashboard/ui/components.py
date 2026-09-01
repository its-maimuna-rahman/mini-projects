"""
UI Visualization Components & Editorial Design System
Implements:
1. Interactive Population Pyramid (Single dataset & Comparative overlays, Percent / Counts)
2. Broad Age Composition Breakdown (Donut chart & Dependency indicator)
3. Data Quality Myers Terminal Digit Preference Visualizer
4. Fertility (ASFR) & Mortality (ASDR) Age Schedules
5. Long-Term Trajectory & Dividend Horizon Time-Series Chart
6. Calm Bell-Curve / Range Indicator Gauges (Clean, rounded card design with zero raw HTML leaks)
"""

from __future__ import annotations
import html
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st


PALETTE = {
    "bg": "#FAF8F5",
    "card": "#FFFFFF",
    "border": "#E2DCD1",
    "text": "#1F1B16",
    "text_muted": "#5A5248",
    "text_light": "#7A7268",
    "male": "#C86446",          # Terracotta Primary
    "female": "#DDA15E",        # Warm Ochre
    "compare_male": "#2E5C78",  # High-contrast Slate Blue
    "compare_female": "#5E7C8D",# Muted Slate
    "teal": "#2A9D8F",          # Balanced / Success Teal
    "normal_band": "rgba(200, 100, 70, 0.12)",
    "alert": "#C05621",         # Deep Amber/Rust Alert
    "success": "#1E7B6E",       # Muted Pine Green
}


def create_population_pyramid(
    df_single_or_5yr: pd.DataFrame,
    title: str = "Population Pyramid by Age & Sex",
    df_compare: Optional[pd.DataFrame] = None,
    compare_label: Optional[str] = None,
    current_label: str = "Current",
    as_percentage: bool = True,
) -> go.Figure:
    """
    Creates an interactive population pyramid with rounded bars,
    crisp high-contrast colors, and optional comparison overlay.
    """
    df = df_single_or_5yr.copy()
    age_col = "age_group" if "age_group" in df.columns else ("age" if "age" in df.columns else df.columns[0])

    if "male" not in df.columns or "female" not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Age distribution table requires 'male' and 'female' columns.", font=dict(family="Inter, sans-serif", size=14)),
            paper_bgcolor=PALETTE["bg"],
            plot_bgcolor=PALETTE["card"],
        )
        return fig

    males = df["male"].values.astype(float)
    females = df["female"].values.astype(float)
    ages = df[age_col].astype(str).values

    total_pop = males.sum() + females.sum()
    if total_pop <= 0:
        total_pop = 1.0

    if as_percentage:
        m_vals = (males / total_pop) * 100.0
        f_vals = (females / total_pop) * 100.0
        x_unit = "%"
        x_title = "Share of Total Population (%)"
    else:
        m_vals = males
        f_vals = females
        x_unit = ""
        x_title = "Population Count"

    fig = go.Figure()

    # Male Bars (Negative x for left side)
    fig.add_trace(go.Bar(
        y=ages,
        x=-m_vals,
        name=f"Males ({current_label})",
        orientation="h",
        marker=dict(
            color=PALETTE["male"],
            line=dict(color="#B35336", width=0.5),
        ),
        customdata=np.stack((males, (males / total_pop) * 100.0), axis=-1),
        hovertemplate="<b>Age %{y} — Male</b><br>Count: %{customdata[0]:,.0f}<br>Share: %{customdata[1]:.2f}%<extra></extra>",
    ))

    # Female Bars (Positive x for right side)
    fig.add_trace(go.Bar(
        y=ages,
        x=f_vals,
        name=f"Females ({current_label})",
        orientation="h",
        marker=dict(
            color=PALETTE["female"],
            line=dict(color="#C88E4B", width=0.5),
        ),
        customdata=np.stack((females, (females / total_pop) * 100.0), axis=-1),
        hovertemplate="<b>Age %{y} — Female</b><br>Count: %{customdata[0]:,.0f}<br>Share: %{customdata[1]:.2f}%<extra></extra>",
    ))

    # Optional Comparison Overlay
    if df_compare is not None and not df_compare.empty:
        c_df = df_compare.copy()
        c_age_col = "age_group" if "age_group" in c_df.columns else ("age" if "age" in c_df.columns else c_df.columns[0])
        if "male" in c_df.columns and "female" in c_df.columns:
            c_males = c_df["male"].values.astype(float)
            c_females = c_df["female"].values.astype(float)
            c_tot = c_males.sum() + c_females.sum()
            if c_tot <= 0:
                c_tot = 1.0

            if as_percentage:
                c_m_vals = (c_males / c_tot) * 100.0
                c_f_vals = (c_females / c_tot) * 100.0
            else:
                c_m_vals = c_males
                c_f_vals = c_females

            c_lbl = compare_label or "Comparison"

            fig.add_trace(go.Scatter(
                y=c_df[c_age_col].astype(str).values,
                x=-c_m_vals,
                mode="lines+markers",
                name=f"Males ({c_lbl})",
                line=dict(color=PALETTE["compare_male"], width=2.2, dash="dash"),
                marker=dict(size=5, color=PALETTE["compare_male"], symbol="circle"),
                customdata=np.stack((c_males, (c_males / c_tot) * 100.0), axis=-1),
                hovertemplate=f"<b>Age %{{y}} — Male ({c_lbl})</b><br>Count: %{{customdata[0]:,.0f}}<br>Share: %{{customdata[1]:.2f}}%<extra></extra>",
            ))

            fig.add_trace(go.Scatter(
                y=c_df[c_age_col].astype(str).values,
                x=c_f_vals,
                mode="lines+markers",
                name=f"Females ({c_lbl})",
                line=dict(color=PALETTE["compare_female"], width=2.2, dash="dash"),
                marker=dict(size=5, color=PALETTE["compare_female"], symbol="circle"),
                customdata=np.stack((c_females, (c_females / c_tot) * 100.0), axis=-1),
                hovertemplate=f"<b>Age %{{y}} — Female ({c_lbl})</b><br>Count: %{{customdata[0]:,.0f}}<br>Share: %{{customdata[1]:.2f}}%<extra></extra>",
            ))

    max_v = max(m_vals.max(), f_vals.max()) * 1.15
    if as_percentage:
        tick_vals = [-round(max_v * 0.8, 1), -round(max_v * 0.4, 1), 0, round(max_v * 0.4, 1), round(max_v * 0.8, 1)]
        tick_text = [f"{abs(v):.1f}%" for v in tick_vals]
    else:
        tick_vals = [-round(max_v * 0.8), -round(max_v * 0.4), 0, round(max_v * 0.4), round(max_v * 0.8)]
        tick_text = [f"{abs(v):,.0f}" for v in tick_vals]

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Newsreader, Georgia, serif", size=18, color=PALETTE["text"]),
            x=0.01,
            y=0.97,
        ),
        barmode="relative",
        bargap=0.12,
        plot_bgcolor=PALETTE["card"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=PALETTE["text"], size=12),
        xaxis=dict(
            title=dict(text=x_title, font=dict(size=11, color=PALETTE["text_muted"])),
            tickmode="array",
            tickvals=tick_vals,
            ticktext=tick_text,
            range=[-max_v, max_v],
            gridcolor=PALETTE["border"],
            zeroline=True,
            zerolinecolor=PALETTE["text_muted"],
            zerolinewidth=1.2,
        ),
        yaxis=dict(
            title=dict(text="Age Group", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor=PALETTE["border"],
            borderwidth=1,
        ),
        margin=dict(l=40, r=40, t=65, b=40),
        height=520,
    )
    return fig


def create_age_composition_donut(
    pop_0_14: float,
    pop_15_64: float,
    pop_65_plus: float,
    title: str = "Broad Age Composition & Dependency Base",
) -> go.Figure:
    """
    Creates a donut chart showing the three demographic functional age segments:
    Youth (0-14), Working-Age (15-64), and Elderly (65+).
    """
    total = pop_0_14 + pop_15_64 + pop_65_plus
    if total <= 0:
        total = 1.0

    working_share = (pop_15_64 / total) * 100.0
    dep_ratio = ((pop_0_14 + pop_65_plus) / pop_15_64 * 100.0) if pop_15_64 > 0 else 0.0

    labels = ["Youth (0–14 yrs)", "Working-Age (15–64 yrs)", "Elderly (65+ yrs)"]
    values = [pop_0_14, pop_15_64, pop_65_plus]
    colors = [PALETTE["female"], PALETTE["male"], PALETTE["compare_male"]]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(
            colors=colors,
            line=dict(color="#FFFFFF", width=2.5),
        ),
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>Population: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Newsreader, Georgia, serif", size=18, color=PALETTE["text"]),
            x=0.02,
            y=0.97,
        ),
        annotations=[
            dict(
                text=f"<b>{working_share:.1f}%</b><br><span style='font-size:11px; color:#5A5248;'>Working-Age</span><br><span style='font-size:10px; color:#7A7268;'>TDR: {dep_ratio:.1f}</span>",
                x=0.5,
                y=0.5,
                font=dict(family="Inter, sans-serif", size=18, color=PALETTE["text"]),
                showarrow=False,
            )
        ],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
        plot_bgcolor=PALETTE["card"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=PALETTE["text"]),
        margin=dict(l=30, r=30, t=60, b=50),
        height=380,
    )
    return fig


def create_digit_preference_chart(
    single_year_df: pd.DataFrame,
    title: str = "Terminal Digit Preference Audit (Myers' 0–9 Analysis)",
) -> go.Figure:
    """
    Visualizes terminal digit attraction (heaping) across digits 0 through 9
    against the theoretical 10.0% unheaped benchmark.
    """
    df = single_year_df.copy()
    age_col = "age" if "age" in df.columns else df.columns[0]
    pop_col = "total" if "total" in df.columns else ("male" if "male" in df.columns else df.columns[1])

    # Filter ages 10 to 69 for standard Myers calculation
    df_10_69 = df[(df[age_col] >= 10) & (df[age_col] <= 69)].copy()
    df_10_69["digit"] = df_10_69[age_col] % 10
    sum1 = df_10_69.groupby("digit")[pop_col].sum().to_dict()

    df_20_69 = df[(df[age_col] >= 20) & (df[age_col] <= 69)].copy()
    df_20_69["digit"] = df_20_69[age_col] % 10
    sum2 = df_20_69.groupby("digit")[pop_col].sum().to_dict()

    blended_counts = {}
    for d in range(10):
        s1 = sum1.get(d, 0.0)
        s2 = sum2.get(d, 0.0)
        blended_counts[d] = ((d + 1) * s1) + ((9 - d) * s2)

    total_blended = sum(blended_counts.values()) or 1.0
    digits = [str(d) for d in range(10)]
    pcts = [(blended_counts[d] / total_blended) * 100.0 for d in range(10)]

    # Color code bars by deviation from 10%
    bar_colors = []
    for p in pcts:
        if p > 12.0:
            bar_colors.append(PALETTE["alert"])  # Heavy heaping
        elif p > 10.5:
            bar_colors.append(PALETTE["male"])   # Moderate heaping
        elif p < 8.5:
            bar_colors.append(PALETTE["compare_male"]) # Avoidance
        else:
            bar_colors.append(PALETTE["teal"])   # Near ideal

    fig = go.Figure()

    # Digit Bars
    fig.add_trace(go.Bar(
        x=digits,
        y=pcts,
        marker=dict(
            color=bar_colors,
            line=dict(color=PALETTE["border"], width=1),
        ),
        customdata=[p - 10.0 for p in pcts],
        hovertemplate="<b>Terminal Digit: %{x}</b><br>Blended Share: %{y:.2f}%<br>Deviation from 10%: %{customdata:+.2f}%<extra></extra>",
    ))

    # Expected 10% benchmark dashed line
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=9.5,
        y0=10.0,
        y1=10.0,
        line=dict(color="#1F1B16", width=1.5, dash="dash"),
    )

    fig.add_annotation(
        x=9.2,
        y=10.6,
        text="Expected: 10.0%",
        showarrow=False,
        font=dict(size=10, color=PALETTE["text_muted"], family="Inter, sans-serif"),
    )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Newsreader, Georgia, serif", size=18, color=PALETTE["text"]),
            x=0.02,
            y=0.97,
        ),
        plot_bgcolor=PALETTE["card"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=PALETTE["text"], size=12),
        xaxis=dict(
            title=dict(text="Terminal Digit (0 to 9)", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
        ),
        yaxis=dict(
            title=dict(text="Blended Population Share (%)", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
            range=[0, max(max(pcts) * 1.25, 16)],
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    return fig


def create_fertility_schedule_chart(
    fertility_df: pd.DataFrame,
    title: str = "Age-Specific Fertility Rates (ASFR Schedule)",
) -> go.Figure:
    """
    Renders maternal age-specific fertility rate curve across 5-year childbearing intervals.
    """
    df = fertility_df.copy()
    if "asfr" not in df.columns and "births" in df.columns and "female_pop" in df.columns:
        df["asfr"] = (df["births"] / df["female_pop"]) * 1000.0

    age_col = "age_group" if "age_group" in df.columns else df.columns[0]
    asfr_col = "asfr" if "asfr" in df.columns else df.columns[1]

    fig = go.Figure()

    # ASFR Spline Area
    fig.add_trace(go.Scatter(
        x=df[age_col],
        y=df[asfr_col],
        mode="lines+markers",
        line=dict(color=PALETTE["male"], width=3, shape="spline"),
        marker=dict(size=7, color=PALETTE["male"]),
        fill="tozeroy",
        fillcolor="rgba(200, 100, 70, 0.12)",
        name="ASFR (per 1,000)",
        hovertemplate="<b>Age Group: %{x}</b><br>ASFR: %{y:.1f} births / 1,000 women<extra></extra>",
    ))

    # Highlight peak fertility
    max_idx = df[asfr_col].idxmax()
    peak_age = df.loc[max_idx, age_col]
    peak_val = df.loc[max_idx, asfr_col]

    fig.add_annotation(
        x=peak_age,
        y=peak_val,
        text=f"<b>Peak: {peak_val:.1f}</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowcolor=PALETTE["male"],
        font=dict(family="Inter, sans-serif", size=11, color=PALETTE["text"]),
        yshift=10,
    )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Newsreader, Georgia, serif", size=18, color=PALETTE["text"]),
            x=0.02,
            y=0.97,
        ),
        plot_bgcolor=PALETTE["card"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=PALETTE["text"], size=12),
        xaxis=dict(
            title=dict(text="Maternal Age Group (Years)", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
        ),
        yaxis=dict(
            title=dict(text="Births per 1,000 Women", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    return fig


def create_mortality_schedule_chart(
    mortality_df: pd.DataFrame,
    title: str = "Age-Specific Death Rate (ASDR Schedule)",
    log_scale: bool = False,
) -> go.Figure:
    """
    Renders demographic mortality curve across age groups (J-shaped / U-shaped curve).
    """
    df = mortality_df.copy()
    if "asdr" not in df.columns and "deaths" in df.columns and "population" in df.columns:
        df["asdr"] = (df["deaths"] / df["population"]) * 1000.0

    age_col = "age_group" if "age_group" in df.columns else df.columns[0]
    asdr_col = "asdr" if "asdr" in df.columns else df.columns[1]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[age_col],
        y=df[asdr_col],
        mode="lines+markers",
        line=dict(color=PALETTE["compare_male"], width=2.8, shape="spline"),
        marker=dict(size=6, color=PALETTE["compare_male"]),
        fill="tozeroy",
        fillcolor="rgba(46, 92, 120, 0.10)",
        name="ASDR (per 1,000)",
        hovertemplate="<b>Age Group: %{x}</b><br>Death Rate: %{y:.2f} per 1,000<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Newsreader, Georgia, serif", size=18, color=PALETTE["text"]),
            x=0.02,
            y=0.97,
        ),
        plot_bgcolor=PALETTE["card"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=PALETTE["text"], size=12),
        xaxis=dict(
            title=dict(text="Age Group", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
        ),
        yaxis=dict(
            title=dict(text="Deaths per 1,000 Population" + (" (Log Scale)" if log_scale else ""), font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
            type="log" if log_scale else "linear",
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    return fig


def create_trajectory_chart(
    combined_df: pd.DataFrame,
    dividend_start_year: Optional[int] = None,
    dividend_end_year: Optional[int] = None,
    title: str = "Long-Term Demographic Trajectory & Transition Horizon",
) -> go.Figure:
    """
    Creates an editorial time-series chart showing historical series (1970-2024)
    and future projections (2025-2054) with dividend window highlight.
    """
    df = combined_df.copy()
    fig = go.Figure()

    df_hist = df[df["is_projected"] == False]
    df_proj = df[df["is_projected"] == True]

    # Working Age Share %
    fig.add_trace(go.Scatter(
        x=df_hist["year"],
        y=df_hist["pct_working_15_64"],
        name="Working-Age (15–64) [Hist]",
        line=dict(color=PALETTE["male"], width=2.8),
        mode="lines",
        hovertemplate="<b>%{x} (Hist)</b><br>Working-Age Share: %{y:.1f}%<extra></extra>",
    ))
    if not df_proj.empty:
        fig.add_trace(go.Scatter(
            x=df_proj["year"],
            y=df_proj["pct_working_15_64"],
            name="Working-Age (Projected)",
            line=dict(color=PALETTE["male"], width=2.8, dash="dash"),
            mode="lines",
            hovertemplate="<b>%{x} (Proj)</b><br>Working-Age Share: %{y:.1f}%<extra></extra>",
        ))

    # Elderly Share %
    fig.add_trace(go.Scatter(
        x=df_hist["year"],
        y=df_hist["pct_elderly_65_plus"],
        name="Elderly (65+) [Hist]",
        line=dict(color=PALETTE["compare_male"], width=2.2),
        mode="lines",
        hovertemplate="<b>%{x} (Hist)</b><br>Elderly Share: %{y:.1f}%<extra></extra>",
    ))
    if not df_proj.empty:
        fig.add_trace(go.Scatter(
            x=df_proj["year"],
            y=df_proj["pct_elderly_65_plus"],
            name="Elderly (Projected)",
            line=dict(color=PALETTE["compare_male"], width=2.2, dash="dash"),
            mode="lines",
            hovertemplate="<b>%{x} (Proj)</b><br>Elderly Share: %{y:.1f}%<extra></extra>",
        ))

    # TFR Line (Secondary Axis)
    fig.add_trace(go.Scatter(
        x=df_hist["year"],
        y=df_hist["tfr"],
        name="TFR (Children / Woman) [Hist]",
        line=dict(color=PALETTE["teal"], width=2),
        yaxis="y2",
        mode="lines",
        hovertemplate="<b>%{x} (Hist)</b><br>TFR: %{y:.2f}<extra></extra>",
    ))
    if not df_proj.empty:
        fig.add_trace(go.Scatter(
            x=df_proj["year"],
            y=df_proj["tfr"],
            name="TFR (Projected)",
            line=dict(color=PALETTE["teal"], width=2, dash="dash"),
            yaxis="y2",
            mode="lines",
            hovertemplate="<b>%{x} (Proj)</b><br>TFR: %{y:.2f}<extra></extra>",
        ))

    # Highlight Demographic Dividend Window (Working Age >= 60%)
    if dividend_start_year and dividend_end_year:
        fig.add_vrect(
            x0=dividend_start_year,
            x1=dividend_end_year,
            fillcolor=PALETTE["normal_band"],
            layer="below",
            line_width=0,
            annotation_text=f"Demographic Dividend Window ({dividend_start_year}–{dividend_end_year})",
            annotation_position="top left",
            annotation=dict(font_size=11, font_color=PALETTE["male"], font_family="Inter, sans-serif"),
        )

    # Present Transition Line
    if not df_hist.empty:
        trans_year = int(df_hist["year"].max())
        fig.add_vline(
            x=trans_year,
            line=dict(color=PALETTE["text_muted"], width=1, dash="dot"),
            annotation_text="Present Transition",
            annotation_position="bottom right",
            annotation=dict(font_size=10, font_color=PALETTE["text_muted"], font_family="Inter, sans-serif"),
        )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Newsreader, Georgia, serif", size=18, color=PALETTE["text"]),
            x=0.02,
            y=0.97,
        ),
        plot_bgcolor=PALETTE["card"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=PALETTE["text"], size=12),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
        ),
        yaxis=dict(
            title=dict(text="Population Share (%)", font=dict(size=11, color=PALETTE["text_muted"])),
            gridcolor=PALETTE["border"],
            range=[0, 80],
        ),
        yaxis2=dict(
            title=dict(text="Total Fertility Rate (TFR)", font=dict(size=11, color=PALETTE["teal"])),
            overlaying="y",
            side="right",
            range=[0, 6.5],
            gridcolor="rgba(0,0,0,0)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor=PALETTE["border"],
            borderwidth=1,
        ),
        margin=dict(l=40, r=40, t=65, b=40),
        height=480,
    )
    return fig


def render_calm_gauge_html(
    measure_name: str,
    value: float,
    formatted_value: str,
    unit: str,
    status: str,
    status_label: str,
    gauge_min: float,
    gauge_max: float,
    source: str,
    is_heuristic: bool = False,
) -> str:
    """
    Renders an editorial calm range indicator in clean, unindented HTML.
    Features rounded corners, soft warm colors, pill tracks, and zero code-block artifacts.
    """
    clamped_val = max(gauge_min, min(gauge_max, value))
    pct = ((clamped_val - gauge_min) / (gauge_max - gauge_min)) * 100.0 if gauge_max > gauge_min else 50.0

    # Color tokens
    badge_bg = "#F2EBE5"
    badge_color = "#C86446"
    if status in ("CRITICAL", "SEVERE"):
        badge_bg = "#FCECE7"
        badge_color = "#C05621"
    elif status == "EXCELLENT":
        badge_bg = "#EBF5F3"
        badge_color = "#1E7B6E"
    elif status == "GOOD":
        badge_bg = "#EEF4F7"
        badge_color = "#2E5C78"
    elif status in ("CONCERNING", "WARNING"):
        badge_bg = "#FAF0EA"
        badge_color = "#C86446"

    tag_label = "(Heuristic Standard)" if is_heuristic else f"({html.escape(source)})"
    
    # Return compact unindented HTML with no multi-space leading indentation
    return (
        f'<div style="background:#FFFFFF;border:1px solid #E2DCD1;border-radius:14px;'
        f'padding:18px 22px;margin-bottom:14px;font-family:Inter,system-ui,-apple-system,sans-serif;'
        f'box-shadow:0 1px 3px rgba(31,27,22,0.03);">'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">'
        f'<div><span style="font-family:Newsreader,Georgia,serif;font-size:17px;font-weight:600;color:#1F1B16;">{html.escape(measure_name)}</span>'
        f'<span style="font-size:11px;color:#7A7268;margin-left:6px;font-weight:500;">{tag_label}</span></div>'
        f'<div style="text-align:right;"><span style="font-size:20px;font-weight:700;color:#1F1B16;font-variant-numeric:tabular-nums;">{html.escape(formatted_value)}</span></div>'
        f'</div>'
        f'<div style="position:relative;margin:16px 0 10px 0;height:10px;background:#EDE7DD;border-radius:9999px;">'
        f'<div style="position:absolute;left:30%;width:40%;height:100%;background:#D5CCC0;border-radius:9999px;"></div>'
        f'<div style="position:absolute;left:calc({pct:.1f}% - 8px);top:-4px;width:18px;height:18px;border-radius:50%;background:{badge_color};border:2.5px solid #FFFFFF;box-shadow:0 1px 4px rgba(0,0,0,0.22);"></div>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;font-size:11px;color:#5A5248;font-weight:500;margin-bottom:8px;">'
        f'<span>{gauge_min:g} {html.escape(unit)}</span>'
        f'<span style="color:#7A7268;font-style:italic;">Standard Reference Horizon</span>'
        f'<span>{gauge_max:g} {html.escape(unit)}</span>'
        f'</div>'
        f'<div style="display:inline-block;padding:4px 12px;border-radius:9999px;background:{badge_bg};color:{badge_color};font-size:11.5px;font-weight:600;">'
        f'{html.escape(status.title())}: {html.escape(status_label)}'
        f'</div>'
        f'</div>'
    )


def render_calm_gauge(
    measure_name: str,
    value: float,
    formatted_value: str,
    unit: str,
    status: str,
    status_label: str,
    gauge_min: float,
    gauge_max: float,
    source: str,
    is_heuristic: bool = False,
):
    """Direct Streamlit renderer for calm gauges using st.html."""
    html_content = render_calm_gauge_html(
        measure_name=measure_name,
        value=value,
        formatted_value=formatted_value,
        unit=unit,
        status=status,
        status_label=status_label,
        gauge_min=gauge_min,
        gauge_max=gauge_max,
        source=source,
        is_heuristic=is_heuristic,
    )
    st.html(html_content)
