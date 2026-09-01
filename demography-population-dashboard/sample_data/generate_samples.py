"""
Sample Dataset Generator for Vital Stats Suite
Generates:
1. sample_data/census_2011.json (Realistic benchmark census)
2. sample_data/census_2022.json (Transitioned modern census for comparison)
3. sample_data/dirty_census.json (Heaped digits & missing columns for quality tests)
4. sample_data/time_series_1970_2024.csv (Historical time series for Module 2 projections)
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import os

OUT_DIR = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Benchmark Census 2011
# Single year age distribution (0-90)
np.random.seed(42)
ages = list(range(91))
# Exponential-logistic realistic population profile
base_cohort = 120000.0
single_males = []
single_females = []

for a in ages:
    surv = np.exp(-0.0005 * a - 0.00004 * (a ** 2))
    m = int(base_cohort * 0.515 * surv * (1.0 + 0.01 * np.sin(a)))
    f = int(base_cohort * 0.485 * surv * (1.0 + 0.01 * np.cos(a)))
    single_males.append(m)
    single_females.append(f)

df_single_2011 = pd.DataFrame({
    "age": ages,
    "male": single_males,
    "female": single_females,
    "total": [m + f for m, f in zip(single_males, single_females)]
})

# 5-Year Age Groups for 2011
age_groups = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85+"
]

# Fertility schedule 2011 (Maternal age 15-49)
fert_groups = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]
fem_pop_fert_2011 = [280000, 270000, 260000, 245000, 230000, 210000, 190000]
asfr_target_2011 = [45.0, 135.0, 120.0, 75.0, 35.0, 12.0, 3.0] # sum = 425 -> TFR = 5 * 425 / 1000 = 2.125
births_2011 = [int(p * r / 1000.0) for p, r in zip(fem_pop_fert_2011, asfr_target_2011)]
fem_births_2011 = [int(b * (100.0 / 205.0)) for b in births_2011]

df_fert_2011 = pd.DataFrame({
    "age_group": fert_groups,
    "female_pop": fem_pop_fert_2011,
    "births": births_2011,
    "female_births": fem_births_2011
})

# Mortality schedule 2011
pop_mort_2011 = [560000, 545000, 530000, 510000, 490000, 470000, 445000, 420000, 385000, 350000, 310000, 265000, 215000, 160000, 110000, 65000, 32000, 14000]
asdr_target_2011 = [4.2, 0.6, 0.4, 0.9, 1.3, 1.6, 2.1, 3.0, 4.5, 6.8, 10.2, 15.5, 23.8, 36.5, 56.0, 85.0, 130.0, 210.0]
deaths_2011 = [int(p * r / 1000.0) for p, r in zip(pop_mort_2011, asdr_target_2011)]

df_mort_2011 = pd.DataFrame({
    "age_group": age_groups,
    "population": pop_mort_2011,
    "deaths": deaths_2011
})

census_2011 = {
    "name": "National Population Census 2011",
    "year": 2011,
    "region": "National",
    "total_population": sum(pop_mort_2011),
    "male_population": int(sum(pop_mort_2011) * 0.508),
    "female_population": int(sum(pop_mort_2011) * 0.492),
    "pop_0_14": sum(pop_mort_2011[0:3]),
    "pop_15_64": sum(pop_mort_2011[3:13]),
    "pop_65_plus": sum(pop_mort_2011[13:]),
    "total_live_births": sum(births_2011),
    "male_births": sum(births_2011) - sum(fem_births_2011),
    "female_births": sum(fem_births_2011),
    "marital_births": int(sum(births_2011) * 0.88),
    "married_women_15_49": int(sum(fem_pop_fert_2011) * 0.68),
    "total_women_15_49": sum(fem_pop_fert_2011),
    "total_deaths": sum(deaths_2011),
    "neonatal_deaths": int(sum(births_2011) * 0.014),
    "infant_deaths": int(sum(births_2011) * 0.024),
    "child_deaths_1_4": int(pop_mort_2011[0] * 0.0018),
    "pop_1_4": int(pop_mort_2011[0] * 0.8),
    "pec_omission_rate": 0.032,
    "pec_completeness_rate": 0.968,
    "single_year_ages": df_single_2011.to_dict(orient="records"),
    "fertility_schedule": df_fert_2011.to_dict(orient="records"),
    "mortality_schedule": df_mort_2011.to_dict(orient="records"),
}

with open(OUT_DIR / "census_2011.json", "w") as f:
    json.dump(census_2011, f, indent=2)


# 2. Modern Census 2022 (Transitioned: lower fertility, aging, lower mortality)
pop_mort_2022 = [420000, 450000, 480000, 510000, 520000, 515000, 495000, 470000, 440000, 410000, 380000, 350000, 310000, 260000, 200000, 140000, 80000, 40000]
fem_pop_fert_2022 = [260000, 265000, 260000, 250000, 235000, 220000, 205000]
asfr_target_2022 = [18.0, 75.0, 110.0, 82.0, 32.0, 8.0, 1.0] # sum = 326 -> TFR = 1.63
births_2022 = [int(p * r / 1000.0) for p, r in zip(fem_pop_fert_2022, asfr_target_2022)]
fem_births_2022 = [int(b * (100.0 / 205.0)) for b in births_2022]

asdr_target_2022 = [2.8, 0.4, 0.3, 0.6, 0.9, 1.1, 1.5, 2.2, 3.4, 5.2, 7.8, 11.9, 18.2, 28.0, 44.0, 68.0, 105.0, 175.0]
deaths_2022 = [int(p * r / 1000.0) for p, r in zip(pop_mort_2022, asdr_target_2022)]

# Single-year 2022
single_males_2022 = []
single_females_2022 = []
for a in ages:
    surv = np.exp(-0.0003 * a - 0.00003 * (a ** 2))
    m = int(95000 * 0.505 * surv * (1.0 + 0.005 * np.sin(a)))
    f = int(95000 * 0.495 * surv * (1.0 + 0.005 * np.cos(a)))
    single_males_2022.append(m)
    single_females_2022.append(f)

df_single_2022 = pd.DataFrame({
    "age": ages,
    "male": single_males_2022,
    "female": single_females_2022,
    "total": [m + f for m, f in zip(single_males_2022, single_females_2022)]
})

df_fert_2022 = pd.DataFrame({
    "age_group": fert_groups,
    "female_pop": fem_pop_fert_2022,
    "births": births_2022,
    "female_births": fem_births_2022
})

df_mort_2022 = pd.DataFrame({
    "age_group": age_groups,
    "population": pop_mort_2022,
    "deaths": deaths_2022
})

census_2022 = {
    "name": "National Population Census 2022",
    "year": 2022,
    "region": "National",
    "total_population": sum(pop_mort_2022),
    "male_population": int(sum(pop_mort_2022) * 0.502),
    "female_population": int(sum(pop_mort_2022) * 0.498),
    "pop_0_14": sum(pop_mort_2022[0:3]),
    "pop_15_64": sum(pop_mort_2022[3:13]),
    "pop_65_plus": sum(pop_mort_2022[13:]),
    "total_live_births": sum(births_2022),
    "male_births": sum(births_2022) - sum(fem_births_2022),
    "female_births": sum(fem_births_2022),
    "marital_births": int(sum(births_2022) * 0.82),
    "married_women_15_49": int(sum(fem_pop_fert_2022) * 0.62),
    "total_women_15_49": sum(fem_pop_fert_2022),
    "total_deaths": sum(deaths_2022),
    "neonatal_deaths": int(sum(births_2022) * 0.006),
    "infant_deaths": int(sum(births_2022) * 0.009),
    "child_deaths_1_4": int(pop_mort_2022[0] * 0.0008),
    "pop_1_4": int(pop_mort_2022[0] * 0.8),
    "pec_omission_rate": 0.018,
    "pec_completeness_rate": 0.982,
    "single_year_ages": df_single_2022.to_dict(orient="records"),
    "fertility_schedule": df_fert_2022.to_dict(orient="records"),
    "mortality_schedule": df_mort_2022.to_dict(orient="records"),
}

with open(OUT_DIR / "census_2022.json", "w") as f:
    json.dump(census_2022, f, indent=2)


# 3. Dirty Dataset (Heaping on 0 and 5 + missing fertility schedule & neonatal deaths)
dirty_single_males = []
dirty_single_females = []
for a in ages:
    base = 50000.0 * np.exp(-0.01 * a)
    # Heavy artificial heaping on multiples of 5 (digits 0 and 5)
    multiplier = 2.4 if (a % 5 == 0) else 0.65
    m = int(base * 0.52 * multiplier)
    f = int(base * 0.48 * multiplier)
    dirty_single_males.append(m)
    dirty_single_females.append(f)

df_dirty_single = pd.DataFrame({
    "age": ages,
    "male": dirty_single_males,
    "female": dirty_single_females,
    "total": [m + f for m, f in zip(dirty_single_males, dirty_single_females)]
})

dirty_dataset = {
    "name": "Historical Dirty Census (High Heaping & Incomplete)",
    "year": 1980,
    "region": "Rural Province B",
    "total_population": int(df_dirty_single["total"].sum()),
    "male_population": int(df_dirty_single["male"].sum()),
    "female_population": int(df_dirty_single["female"].sum()),
    "pop_0_14": int(df_dirty_single[df_dirty_single["age"] <= 14]["total"].sum()),
    "pop_15_64": int(df_dirty_single[(df_dirty_single["age"] >= 15) & (df_dirty_single["age"] <= 64)]["total"].sum()),
    "pop_65_plus": int(df_dirty_single[df_dirty_single["age"] >= 65]["total"].sum()),
    "total_live_births": 75000,
    "total_deaths": 22000,
    "infant_deaths": 3800,
    "pec_omission_rate": 0.085, # 8.5% undercount
    "pec_completeness_rate": 0.915,
    "single_year_ages": df_dirty_single.to_dict(orient="records"),
    # Missing: fertility_schedule, mortality_schedule, married_women_15_49, neonatal_deaths
}

with open(OUT_DIR / "dirty_census.json", "w") as f:
    json.dump(dirty_dataset, f, indent=2)


# 4. Historical Time Series (1970 - 2024)
years = list(range(1970, 2025))
ts_data = []
pop = 45.0  # Millions
for y in years:
    t = y - 1970
    # Logistic fertility transition
    tfr = 5.6 / (1.0 + np.exp(0.08 * (t - 22))) + 1.35
    cbr = tfr * 6.8 + 2.5
    # Epidemiologic mortality transition
    imr = 110.0 * np.exp(-0.045 * t) + 6.0
    u5mr = imr * 1.45
    cdr = 16.5 * np.exp(-0.03 * t) + 6.2 + (0.05 * t if t > 35 else 0) # aging effect in later years
    life_exp = 52.0 + 31.0 / (1.0 + np.exp(-0.07 * (t - 20)))
    
    growth_rate = (cbr - cdr) / 10.0
    pop = pop * (1.0 + growth_rate / 100.0)
    
    # Age structure shifts
    pct_young = 44.0 * np.exp(-0.015 * t)
    pct_elderly = 3.5 + 0.25 * t * (1.0 + 0.02 * t)
    pct_working = 100.0 - pct_young - pct_elderly
    
    tdr = ((pct_young + pct_elderly) / pct_working) * 100.0
    oadr = (pct_elderly / pct_working) * 100.0
    
    ts_data.append({
        "year": y,
        "total_population_millions": round(pop, 3),
        "cbr": round(cbr, 2),
        "cdr": round(cdr, 2),
        "tfr": round(tfr, 2),
        "imr": round(imr, 2),
        "u5mr": round(u5mr, 2),
        "life_expectancy": round(life_exp, 1),
        "pct_young_0_14": round(pct_young, 2),
        "pct_working_15_64": round(pct_working, 2),
        "pct_elderly_65_plus": round(pct_elderly, 2),
        "tdr": round(tdr, 2),
        "oadr": round(oadr, 2),
    })

pd.DataFrame(ts_data).to_csv(OUT_DIR / "time_series_1970_2024.csv", index=False)
print("Successfully generated all sample datasets.")
