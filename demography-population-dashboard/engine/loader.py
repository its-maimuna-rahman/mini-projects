"""
Vital Stats Suite - Demographic Data Ingestion & Parser
Supports:
1. Multi-format CSV ingestion (Age-Sex tables, 5-year tables, key-value indicators, wide summaries)
2. JSON dataset ingestion
3. Smart column normalizer and demographic aggregator
4. Sample CSV template generators
"""

from __future__ import annotations
import io
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np

from engine.base import DemographicDataset


def normalize_column_name(col: str) -> str:
    """Normalizes string column names (lowercase, stripped, alphanumeric with underscores)."""
    return re.sub(r"[^a-z0-9_]+", "_", str(col).strip().lower()).strip("_")


def parse_age_to_numeric(val: Any) -> Optional[int]:
    """Extracts base integer age from strings like '0', '5', '85+', '0-4', '5-9'."""
    s = str(val).strip()
    match = re.match(r"^(\d+)", s)
    if match:
        return int(match.group(1))
    return None


def parse_age_group_label(val: Any) -> str:
    """Standardizes age group labels like '0-4', '5 to 9', '85+', '85 and over'."""
    s = str(val).strip()
    if re.match(r"^\d+\s*-\s*\d+$", s):
        parts = re.split(r"\s*-\s*", s)
        return f"{parts[0]}-{parts[1]}"
    if re.match(r"^\d+\s*to\s*\d+$", s, re.IGNORECASE):
        parts = re.split(r"\s+to\s+", s, flags=re.IGNORECASE)
        return f"{parts[0]}-{parts[1]}"
    if "+" in s or "over" in s.lower() or "plus" in s.lower():
        match = re.search(r"(\d+)", s)
        if match:
            return f"{match.group(1)}+"
    return s


def load_demographic_dataset(
    source: Union[str, Path, io.BytesIO, io.StringIO, pd.DataFrame, dict],
    name: Optional[str] = None,
    year: Optional[int] = None,
    region: Optional[str] = None,
) -> DemographicDataset:
    """
    Universal demographic loader. Ingests JSON, CSV (Age-Sex, Key-Value, Wide), or DataFrame,
    and returns a standardized DemographicDataset with full derived structures.
    """
    # 1. Handle JSON string or file path
    if isinstance(source, (str, Path)):
        is_path = False
        if isinstance(source, Path):
            is_path = source.is_file()
            p = source
        elif isinstance(source, str) and "\n" not in source and len(source) < 500:
            try:
                p = Path(source)
                is_path = p.is_file()
            except Exception:
                is_path = False
        
        if is_path:
            if p.suffix.lower() == ".json":
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return _from_dict(data, default_name=name or p.stem, default_year=year, default_region=region)
            else:
                df = pd.read_csv(p)
                return _from_dataframe(df, name=name or p.stem, year=year, region=region)
        else:
            # Check if string is raw JSON
            raw_str = str(source).strip()
            if raw_str.startswith("{") and raw_str.endswith("}"):
                data = json.loads(raw_str)
                return _from_dict(data, default_name=name, default_year=year, default_region=region)
            else:
                # Treat as CSV text
                df = pd.read_csv(io.StringIO(raw_str))
                return _from_dataframe(df, name=name, year=year, region=region)

    # 2. Handle BytesIO / StringIO (from Streamlit file uploader)
    if isinstance(source, (io.BytesIO, io.StringIO)):
        # Inspect first bytes/chars to see if JSON or CSV
        if isinstance(source, io.BytesIO):
            content = source.getvalue().decode("utf-8", errors="replace").strip()
        else:
            content = source.getvalue().strip()

        if content.startswith("{") and content.endswith("}"):
            data = json.loads(content)
            return _from_dict(data, default_name=name, default_year=year, default_region=region)
        else:
            df = pd.read_csv(io.StringIO(content))
            return _from_dataframe(df, name=name, year=year, region=region)

    # 3. Handle Dictionary
    if isinstance(source, dict):
        return _from_dict(source, default_name=name, default_year=year, default_region=region)

    # 4. Handle pandas DataFrame
    if isinstance(source, pd.DataFrame):
        return _from_dataframe(source, name=name, year=year, region=region)

    raise ValueError(f"Unsupported source format for demographic dataset: {type(source)}")


def _from_dict(data: dict, default_name: Optional[str] = None, default_year: Optional[int] = None, default_region: Optional[str] = None) -> DemographicDataset:
    """Builds DemographicDataset from a parsed JSON dictionary."""
    single_year_df = pd.DataFrame(data["single_year_ages"]) if "single_year_ages" in data and data["single_year_ages"] else None
    age_group_5yr_df = pd.DataFrame(data["age_group_5yr"]) if "age_group_5yr" in data and data["age_group_5yr"] else None
    fertility_df = pd.DataFrame(data["fertility_schedule"]) if "fertility_schedule" in data and data["fertility_schedule"] else None
    mortality_df = pd.DataFrame(data["mortality_schedule"]) if "mortality_schedule" in data and data["mortality_schedule"] else None

    # Derive broad age groups if single_year_ages is present but broad groups are missing
    pop_0_14 = data.get("pop_0_14")
    pop_15_64 = data.get("pop_15_64")
    pop_65_plus = data.get("pop_65_plus")
    tot_pop = data.get("total_population")
    male_pop = data.get("male_population")
    fem_pop = data.get("female_population")

    if single_year_df is not None and not single_year_df.empty:
        age_col = "age" if "age" in single_year_df.columns else single_year_df.columns[0]
        single_year_df["age_num"] = single_year_df[age_col].apply(parse_age_to_numeric)
        
        if pop_0_14 is None:
            pop_0_14 = float(single_year_df[single_year_df["age_num"] <= 14]["total"].sum()) if "total" in single_year_df.columns else None
        if pop_15_64 is None:
            pop_15_64 = float(single_year_df[(single_year_df["age_num"] >= 15) & (single_year_df["age_num"] <= 64)]["total"].sum()) if "total" in single_year_df.columns else None
        if pop_65_plus is None:
            pop_65_plus = float(single_year_df[single_year_df["age_num"] >= 65]["total"].sum()) if "total" in single_year_df.columns else None
            
        if tot_pop is None and "total" in single_year_df.columns:
            tot_pop = float(single_year_df["total"].sum())
        if male_pop is None and "male" in single_year_df.columns:
            male_pop = float(single_year_df["male"].sum())
        if fem_pop is None and "female" in single_year_df.columns:
            fem_pop = float(single_year_df["female"].sum())

    return DemographicDataset(
        name=default_name or data.get("name", "Demographic Dataset"),
        year=default_year or data.get("year"),
        region=default_region or data.get("region", "National"),
        total_population=tot_pop,
        male_population=male_pop,
        female_population=fem_pop,
        pop_0_14=pop_0_14,
        pop_15_64=pop_15_64,
        pop_65_plus=pop_65_plus,
        total_live_births=data.get("total_live_births"),
        male_births=data.get("male_births"),
        female_births=data.get("female_births"),
        marital_births=data.get("marital_births"),
        married_women_15_49=data.get("married_women_15_49"),
        total_women_15_49=data.get("total_women_15_49"),
        total_deaths=data.get("total_deaths"),
        male_deaths=data.get("male_deaths"),
        female_deaths=data.get("female_deaths"),
        neonatal_deaths=data.get("neonatal_deaths"),
        infant_deaths=data.get("infant_deaths"),
        child_deaths_1_4=data.get("child_deaths_1_4"),
        pop_1_4=data.get("pop_1_4"),
        pec_omission_rate=data.get("pec_omission_rate"),
        pec_completeness_rate=data.get("pec_completeness_rate"),
        single_year_ages=single_year_df,
        age_group_5yr=age_group_5yr_df,
        fertility_schedule=fertility_df,
        mortality_schedule=mortality_df,
        metadata=data.get("metadata", {}),
    )


def _from_dataframe(
    df: pd.DataFrame,
    name: Optional[str] = None,
    year: Optional[int] = None,
    region: Optional[str] = None,
) -> DemographicDataset:
    """
    Smart CSV / DataFrame Ingestion Engine.
    Detects whether the DataFrame is:
    1. Key-Value Indicator Pair table (e.g. col1 = 'indicator', col2 = 'value')
    2. Single-Row Wide Summary Table (columns = indicators)
    3. Age-Sex Distribution Table (columns: age/age_group, male, female, etc.)
    """
    clean_df = df.copy()
    col_map = {c: normalize_column_name(c) for c in clean_df.columns}
    clean_df.rename(columns=col_map, inplace=True)

    # 1. Check if Key-Value Pair table (e.g. 2 columns: indicator and value)
    if clean_df.shape[1] == 2 and any(c in clean_df.columns for c in ["indicator", "metric", "variable", "parameter", "key"]):
        key_col = [c for c in clean_df.columns if c in ["indicator", "metric", "variable", "parameter", "key"]][0]
        val_col = [c for c in clean_df.columns if c != key_col][0]
        
        kv_dict = {}
        for _, row in clean_df.iterrows():
            k = normalize_column_name(row[key_col])
            v = row[val_col]
            # Attempt numeric conversion
            try:
                if str(v).replace(".", "", 1).replace("-", "", 1).isdigit():
                    v = float(v) if "." in str(v) else int(v)
            except Exception:
                pass
            kv_dict[k] = v
            
        return _from_dict(kv_dict, default_name=name or "Uploaded Dataset", default_year=year, default_region=region)

    # 2. Check if Single-Row Wide Summary Table (e.g. 1 row with columns like total_population, pop_0_14)
    if len(clean_df) == 1 and any(c in clean_df.columns for c in ["total_population", "male_population", "total_deaths", "total_live_births"]):
        kv_dict = clean_df.iloc[0].to_dict()
        return _from_dict(kv_dict, default_name=name or "Uploaded Dataset", default_year=year, default_region=region)

    # 3. Age-Sex Distribution Table
    # Identify Age Column
    age_col = None
    for cand in ["age", "age_group", "agegroup", "age_range", "ages"]:
        if cand in clean_df.columns:
            age_col = cand
            break
            
    if age_col is None:
        # Check first column
        first_col = clean_df.columns[0]
        age_col = first_col

    # Identify Male, Female, Total columns
    male_col = None
    for cand in ["male", "males", "pop_male", "pop_m", "male_population", "men", "boys"]:
        if cand in clean_df.columns:
            male_col = cand
            break
            
    female_col = None
    for cand in ["female", "females", "pop_female", "pop_f", "female_population", "women", "girls"]:
        if cand in clean_df.columns:
            female_col = cand
            break
            
    total_col = None
    for cand in ["total", "total_pop", "total_population", "population", "pop", "both_sexes", "all"]:
        if cand in clean_df.columns:
            total_col = cand
            break

    # Clean numeric data in male/female/total
    for col in [male_col, female_col, total_col]:
        if col and col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce").fillna(0)

    # If male & female exist but total does not, create total
    if male_col and female_col and (not total_col or total_col not in clean_df.columns):
        clean_df["total"] = clean_df[male_col] + clean_df[female_col]
        total_col = "total"
    elif total_col and male_col and not female_col:
        clean_df["female"] = clean_df[total_col] - clean_df[male_col]
        female_col = "female"
    elif total_col and female_col and not male_col:
        clean_df["male"] = clean_df[total_col] - clean_df[female_col]
        male_col = "male"

    # Identify Deaths & Births if present
    deaths_col = None
    for cand in ["deaths", "death", "death_count", "total_deaths", "mortality"]:
        if cand in clean_df.columns:
            deaths_col = cand
            clean_df[deaths_col] = pd.to_numeric(clean_df[deaths_col].astype(str).str.replace(",", "").str.strip(), errors="coerce").fillna(0)
            break

    births_col = None
    for cand in ["births", "birth", "birth_count", "total_births", "live_births"]:
        if cand in clean_df.columns:
            births_col = cand
            clean_df[births_col] = pd.to_numeric(clean_df[births_col].astype(str).str.replace(",", "").str.strip(), errors="coerce").fillna(0)
            break

    female_births_col = None
    for cand in ["female_births", "f_births", "girl_births"]:
        if cand in clean_df.columns:
            female_births_col = cand
            clean_df[female_births_col] = pd.to_numeric(clean_df[female_births_col].astype(str).str.replace(",", "").str.strip(), errors="coerce").fillna(0)
            break

    # Determine if single-year or 5-year age groups
    is_single_year = False
    numeric_ages = clean_df[age_col].apply(parse_age_to_numeric)
    
    # If consecutive integers from 0..50+, it's single year
    valid_nums = numeric_ages.dropna().values
    if len(valid_nums) >= 20 and np.all(np.diff(valid_nums[:15]) == 1):
        is_single_year = True

    single_year_df = None
    age_group_5yr_df = None
    fertility_schedule_df = None
    mortality_schedule_df = None

    if is_single_year:
        single_year_df = pd.DataFrame({
            "age": numeric_ages.astype(int),
            "male": clean_df[male_col].values if male_col else 0,
            "female": clean_df[female_col].values if female_col else 0,
            "total": clean_df[total_col].values if total_col else (clean_df[male_col] + clean_df[female_col]).values,
        })
        # Build 5-year aggregated schedule
        groups = []
        for a in range(0, 85, 5):
            lbl = f"{a}-{a+4}"
            sub = single_year_df[(single_year_df["age"] >= a) & (single_year_df["age"] <= a + 4)]
            groups.append({
                "age_group": lbl,
                "male": sub["male"].sum(),
                "female": sub["female"].sum(),
                "total": sub["total"].sum(),
            })
        # 85+
        sub85 = single_year_df[single_year_df["age"] >= 85]
        groups.append({
            "age_group": "85+",
            "male": sub85["male"].sum(),
            "female": sub85["female"].sum(),
            "total": sub85["total"].sum(),
        })
        age_group_5yr_df = pd.DataFrame(groups)
    else:
        # 5-Year age groups table
        clean_labels = clean_df[age_col].apply(parse_age_group_label)
        age_group_5yr_df = pd.DataFrame({
            "age_group": clean_labels,
            "male": clean_df[male_col].values if male_col else 0,
            "female": clean_df[female_col].values if female_col else 0,
            "total": clean_df[total_col].values if total_col else (clean_df[male_col] + clean_df[female_col]).values,
        })

    # Derive fertility schedule if births exist or can be extracted
    if age_group_5yr_df is not None:
        fert_labels = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]
        fert_sub = age_group_5yr_df[age_group_5yr_df["age_group"].isin(fert_labels)].copy()
        
        if births_col and births_col in clean_df.columns:
            # Map births
            fert_rows = []
            for _, r in clean_df.iterrows():
                lbl = parse_age_group_label(r[age_col])
                if lbl in fert_labels:
                    f_pop = r[female_col] if female_col else r[total_col] * 0.49
                    b = r[births_col]
                    fb = r[female_births_col] if female_births_col else b * (100.0 / 205.0)
                    fert_rows.append({
                        "age_group": lbl,
                        "female_pop": f_pop,
                        "births": b,
                        "female_births": fb,
                    })
            if fert_rows:
                fertility_schedule_df = pd.DataFrame(fert_rows)

    # Derive mortality schedule if deaths exist
    if deaths_col and deaths_col in clean_df.columns and age_group_5yr_df is not None:
        mort_rows = []
        for _, r in clean_df.iterrows():
            lbl = parse_age_group_label(r[age_col])
            pop_val = r[total_col] if total_col else (r[male_col] + r[female_col] if male_col and female_col else 0)
            d_val = r[deaths_col]
            mort_rows.append({
                "age_group": lbl,
                "population": pop_val,
                "deaths": d_val,
            })
        if mort_rows:
            mortality_schedule_df = pd.DataFrame(mort_rows)

    # Compute Broad Age Groups
    tot_pop = float(age_group_5yr_df["total"].sum()) if age_group_5yr_df is not None else float(clean_df[total_col].sum())
    tot_male = float(age_group_5yr_df["male"].sum()) if age_group_5yr_df is not None and male_col else None
    tot_female = float(age_group_5yr_df["female"].sum()) if age_group_5yr_df is not None and female_col else None

    # Calculate 0-14, 15-64, 65+
    pop_0_14 = 0.0
    pop_15_64 = 0.0
    pop_65_plus = 0.0

    if single_year_df is not None:
        pop_0_14 = float(single_year_df[single_year_df["age"] <= 14]["total"].sum())
        pop_15_64 = float(single_year_df[(single_year_df["age"] >= 15) & (single_year_df["age"] <= 64)]["total"].sum())
        pop_65_plus = float(single_year_df[single_year_df["age"] >= 65]["total"].sum())
    elif age_group_5yr_df is not None:
        for _, r in age_group_5yr_df.iterrows():
            lbl = str(r["age_group"])
            pop = float(r["total"])
            num = parse_age_to_numeric(lbl)
            if num is not None:
                if num < 15:
                    pop_0_14 += pop
                elif 15 <= num < 65:
                    pop_15_64 += pop
                else:
                    pop_65_plus += pop

    # Calculate total births / deaths if present
    tot_births = float(clean_df[births_col].sum()) if births_col else (float(fertility_schedule_df["births"].sum()) if fertility_schedule_df is not None else None)
    tot_deaths = float(clean_df[deaths_col].sum()) if deaths_col else (float(mortality_schedule_df["deaths"].sum()) if mortality_schedule_df is not None else None)

    # Married women approximation if women 15-49 available
    women_15_49 = None
    if age_group_5yr_df is not None:
        fert_labels = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]
        w_sub = age_group_5yr_df[age_group_5yr_df["age_group"].isin(fert_labels)]
        if not w_sub.empty:
            women_15_49 = float(w_sub["female"].sum())

    return DemographicDataset(
        name=name or "Uploaded CSV Dataset",
        year=year or 2024,
        region=region or "National",
        total_population=tot_pop,
        male_population=tot_male,
        female_population=tot_female,
        pop_0_14=pop_0_14 if pop_0_14 > 0 else None,
        pop_15_64=pop_15_64 if pop_15_64 > 0 else None,
        pop_65_plus=pop_65_plus if pop_65_plus > 0 else None,
        total_live_births=tot_births,
        total_deaths=tot_deaths,
        total_women_15_49=women_15_49,
        married_women_15_49=int(women_15_49 * 0.65) if women_15_49 else None,
        marital_births=int(tot_births * 0.85) if tot_births else None,
        single_year_ages=single_year_df,
        age_group_5yr=age_group_5yr_df,
        fertility_schedule=fertility_schedule_df,
        mortality_schedule=mortality_schedule_df,
        raw_df=clean_df,
    )


def generate_sample_age_distribution_csv() -> str:
    """Returns a ready-to-use sample CSV template containing 5-year age groups with births and deaths."""
    sample_data = """age_group,male,female,total,births,deaths
0-4,495000,475000,970000,0,3200
5-9,510000,490000,1000000,0,450
10-14,525000,505000,1030000,0,380
15-19,530000,515000,1045000,24000,520
20-24,520000,510000,1030000,68000,690
25-29,500000,495000,995000,72000,820
30-34,475000,470000,945000,41000,980
35-39,440000,435000,875000,16500,1250
40-44,400000,395000,795000,3500,1720
45-49,360000,355000,715000,400,2450
50-54,315000,310000,625000,0,3600
55-59,265000,260000,525000,0,5100
60-64,210000,210000,420000,0,7400
65-69,155000,160000,315000,0,10200
70-74,105000,115000,220000,0,13500
75-79,65000,75000,140000,0,16200
80-84,32000,42000,74000,0,15800
85+,18000,28000,46000,0,17200
"""
    return sample_data.strip()


def generate_sample_summary_csv() -> str:
    """Returns a ready-to-use key-value indicators CSV template."""
    sample_data = """indicator,value
name,Sample Demographic Census 2024
year,2024
region,National
total_population,11765000
male_population,5920000
female_population,5845000
pop_0_14,3000000
pop_15_64,7985000
pop_65_plus,780000
total_live_births,225400
male_births,115900
female_births,109500
marital_births,191590
married_women_15_49,2067000
total_women_15_49,3180000
total_deaths,100860
infant_deaths,4800
neonatal_deaths,2900
child_deaths_1_4,1600
pec_omission_rate,0.028
pec_completeness_rate,0.972
"""
    return sample_data.strip()
