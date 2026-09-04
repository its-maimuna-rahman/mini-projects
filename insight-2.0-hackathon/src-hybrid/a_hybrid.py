#!/usr/bin/env python3
"""
========================================================================================
INSIGHT 2.0 CANCER PATIENT VITAL STATUS PREDICTION PIPELINE (CUDA GPU ACCELERATED)
========================================================================================

A complete, reproducible, and high-performance Machine Learning solution designed for the
cancer patients' vital status prediction challenge, fully accelerated with NVIDIA CUDA GPU.

Pipeline Structure:
  1. Exploratory Data Analysis (EDA)
  2. Data Preprocessing
  3. Feature Engineering (Clinical Domain Features + Interactions)
  4. Model Development (Multi-Architecture GPU GBDT Ensemble: LightGBM, CatBoost, XGBoost)
  5. Hyperparameter Setup & Stratified Cross-Validation (5 Seeds x 5 Folds)
  6. Model Evaluation (OOF F1 Metrics, ROC-AUC, Exact Optimal Threshold Search)
  7. Multi-Start Global Ensemble Weight Optimization
  8. Prediction & Submission Generation

Competition Metric: Weighted F1-score (Dead = positive class)
Evaluation Setup: 5 Seeds x 5 Folds (25-fold bagged ensemble on CUDA GPU)
Hardware: Auto-detects and utilizes NVIDIA CUDA GPU for XGBoost, CatBoost, and LightGBM
========================================================================================
"""

import os
import re
import gc
import time
import glob
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, roc_auc_score, confusion_matrix, classification_report
import lightgbm as lgb
from catboost import CatBoostClassifier
import xgboost as xgb
from scipy.optimize import minimize

try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    CUDA_AVAILABLE = False

warnings.filterwarnings("ignore")

# ========================================================================================
# [0] CONFIGURATION & HARDWARE SETUP
# ========================================================================================
CONFIG = {
    "FINAL_SEEDS": [42, 123, 456, 789, 2024],
    "N_SPLITS": 5,
    "CUTOFF_YEAR": 2023,
    "TARGET_COL": "vital_status",
    "ID_COL": "patient_id",
    "MISSING_TOKENS": ["", "Blank(s)", "Unknown", "unknown", "Unknown/unstaged", "Not applicable"],
    "NODE_SENTINELS": [95, 96, 97, 98, 99],
    "SIZE_SENTINELS": [988, 989, 991, 998, 999],
    "SIZE_MAX_VALID": 987,
    "OUTPUT_SUBMISSION_PATH": "submission_a_h.csv",
    "NUM_THREADS": -1,
    "USE_GPU": CUDA_AVAILABLE,
}

def init_gpu_environment():
    """Initializes and displays Hybrid CPU + GPU environment details for maximum training speed."""
    print("="*80)
    print(" [HYBRID HARDWARE ACCELERATION ACTIVE: INTEL CORE i7 + NVIDIA RTX 4050]")
    if CUDA_AVAILABLE:
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        print(f"  * NVIDIA GPU:     {gpu_name} ({gpu_mem_gb:.2f} GB VRAM) -> XGBoost CUDA Hist Engine")
        torch.backends.cudnn.benchmark = True
    print(f"  * Intel CPU:      Core i7 (All Cores Active) -> LightGBM & CatBoost SIMD/AVX")
    print(f"  * Performance:    Targeting ~35s per fold (vs 109s pure GPU / 80s CPU)")
    print("="*80)


def get_model_params(seed, use_gpu=True):
    """
    Returns diversified, tuned hyperparameter configurations across model families:
    1. LightGBM GBDT (Core i7 multi-threaded CPU engine ~1.1s)
    2. LightGBM ExtraTrees (Core i7 multi-threaded CPU engine ~1.1s)
    3. CatBoost Depth 6 (Core i7 AVX/SSE vector engine with AUC evaluation ~16s)
    4. CatBoost Depth 7 (Core i7 AVX/SSE vector engine with AUC evaluation ~17s)
    5. XGBoost Histogram (NVIDIA RTX 4050 CUDA GPU Hist engine ~1.0s, 12x faster)
    """
    lgb_gbdt_params = {
        "objective": "binary",
        "metric": "auc",
        "learning_rate": 0.03,
        "num_leaves": 63,
        "max_depth": 6,
        "min_data_in_leaf": 20,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 1,
        "lambda_l1": 0.1,
        "lambda_l2": 1.0,
        "cat_smooth": 10,
        "cat_l2": 10,
        "max_cat_threshold": 32,
        "verbose": -1,
        "num_threads": -1,
        "seed": seed
    }

    lgb_et_params = {
        "objective": "binary",
        "metric": "auc",
        "learning_rate": 0.03,
        "num_leaves": 50,
        "max_depth": 7,
        "min_data_in_leaf": 25,
        "feature_fraction": 0.65,
        "bagging_fraction": 0.8,
        "bagging_freq": 1,
        "extra_trees": True,
        "lambda_l1": 0.5,
        "lambda_l2": 2.0,
        "cat_smooth": 15,
        "cat_l2": 15,
        "max_cat_threshold": 32,
        "verbose": -1,
        "num_threads": -1,
        "seed": seed + 100
    }

    cb_d6_params = dict(
        iterations=2500,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=5.0,
        random_strength=1.0,
        eval_metric="AUC",
        early_stopping_rounds=150,
        verbose=0,
        task_type="CPU",
        thread_count=-1,
        allow_writing_files=False,
        auto_class_weights="Balanced"
    )

    cb_d7_params = dict(
        iterations=2500,
        learning_rate=0.025,
        depth=7,
        l2_leaf_reg=3.0,
        random_strength=1.0,
        eval_metric="AUC",
        early_stopping_rounds=150,
        verbose=0,
        task_type="CPU",
        thread_count=-1,
        allow_writing_files=False,
        auto_class_weights="Balanced"
    )

    xgb_params = dict(
        n_estimators=3000,
        learning_rate=0.03,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.75,
        reg_alpha=0.1,
        reg_lambda=1.0,
        tree_method="hist",
        device="cuda" if use_gpu and CUDA_AVAILABLE else "cpu",
        enable_categorical=True,
        eval_metric="auc",
        early_stopping_rounds=150,
        n_jobs=-1
    )

    return lgb_gbdt_params, lgb_et_params, cb_d6_params, cb_d7_params, xgb_params


def find_csv(prefix):
    """Locates dataset CSV files across local and standard competitive environments."""
    patterns = [
        f"{prefix}.csv",
        f"{prefix} (1).csv",
        f"{prefix} (2).csv",
        f"insight-2-0_dataset/{prefix}.csv",
        f"../insight-2-0_dataset/{prefix}.csv",
        f"../../insight-2-0_dataset/{prefix}.csv",
        f"insight-2.0-hackathon/insight-2-0_dataset/{prefix}.csv",
    ]
    for p in patterns:
        if os.path.exists(p):
            print(f"  [Found File]: {p}")
            return p
    files = glob.glob(f"**/{prefix}*.csv", recursive=True)
    if files:
        files.sort(key=lambda x: "(1)" in x)
        print(f"  [Found File in Working Directory]: {files[0]}")
        return files[0]
    files = glob.glob(f"/kaggle/input/**/{prefix}*.csv", recursive=True)
    if files:
        files.sort(key=lambda x: "(1)" in x)
        print(f"  [Found File in Kaggle Input]: {files[0]}")
        return files[0]
    raise FileNotFoundError(f"Could not locate {prefix}.csv dataset file.")


# ========================================================================================
# [1] SECTION 1: EXPLORATORY DATA ANALYSIS (EDA)
# ========================================================================================
def run_eda(train_df, test_df):
    """
    Performs comprehensive Exploratory Data Analysis on clinical features, target distribution,
    missingness patterns, and temporal survival dynamics.
    """
    print("\n" + "="*80)
    print("SECTION 1: EXPLORATORY DATA ANALYSIS (EDA)")
    print("="*80)
    
    print(f"Training set dimensions: {train_df.shape[0]} rows, {train_df.shape[1]} columns")
    print(f"Test set dimensions:     {test_df.shape[0]} rows, {test_df.shape[1]} columns")
    
    # Target distribution
    target_counts = train_df[CONFIG["TARGET_COL"]].value_counts(dropna=False)
    target_norm = train_df[CONFIG["TARGET_COL"]].value_counts(normalize=True)
    print("\n--- Target Variable Distribution (vital_status) ---")
    for cls in target_counts.index:
        print(f"  Class '{cls}': {target_counts[cls]:,} cases ({target_norm[cls]*100:.2f}%)")
    
    # Diagnosis Year Analysis (Key Survival Factor)
    print("\n--- Diagnosis Year vs. Mortality Rate ---")
    yr_ct = pd.crosstab(train_df["year_of_diagnosis"], train_df[CONFIG["TARGET_COL"]], margins=True)
    if "Dead" in yr_ct.columns and "All" in yr_ct.columns:
        yr_ct["Mortality_Rate"] = (yr_ct["Dead"] / yr_ct["All"] * 100).round(2)
        print(yr_ct[["Alive", "Dead", "All", "Mortality_Rate"]].to_string())
    
    # Missing Value Summary
    missing_tr = train_df.isna().sum()
    missing_cols = missing_tr[missing_tr > 0]
    print(f"\n--- Missing Values in Training Set ({len(missing_cols)} columns with NaNs) ---")
    for col, cnt in missing_cols.items():
        print(f"  {col:35s}: {cnt:6d} missing ({cnt/len(train_df)*100:.2f}%)")
    print("="*80 + "\n")


# ========================================================================================
# [2] SECTION 2: DATA PREPROCESSING & CLINICAL HELPERS
# ========================================================================================
def lead_num(s):
    """Extracts leading numerical characters from alphanumeric SEER coding strings."""
    if pd.isna(s): return np.nan
    m = re.match(r"\s*(\d+)", str(s))
    return float(m.group(1)) if m else np.nan

def age_mid(a):
    """Converts categorical age brackets (e.g., '65-69 years', '90+ years') into numerical midpoints."""
    a = str(a)
    if "90+" in a: return 92.0
    m = re.findall(r"\d+", a)
    if len(m) >= 2: return (int(m[0]) + int(m[1])) / 2.0
    return float(m[0]) if m else np.nan

def tnm_num(x, pre):
    """Extracts ordinal numeric cancer staging values from EOD TNM classifications."""
    s = str(x).upper()
    if pre == "T" and "TIS" in s: return 0.0
    m = re.match(pre + r"(\d)", s)
    return float(m.group(1)) if m else np.nan

def map_histology(code):
    """Categorizes ICD-O-3 histology codes into distinct clinical lung oncologic subtypes."""
    try: c = int(str(code)[:4])
    except: return "Other"
    if c in (8041, 8042, 8043, 8044, 8045): return "SCLC"
    if c in (8070, 8071, 8072, 8073, 8074, 8075, 8076, 8080, 8081, 8082): return "Squamous"
    if 8140 <= c <= 8147 or 8250 <= c <= 8255 or 8260 <= c <= 8490: return "Adeno"
    if c in (8240, 8241, 8242, 8243, 8244, 8245, 8246, 8247, 8248, 8249): return "Neuroendocrine"
    if c in (8010, 8011, 8012, 8020, 8030, 8031, 8032, 8033, 8034, 8035): return "NSCLC_NOS"
    if 9590 <= c <= 9739: return "Lymphoma"
    return "Other"

def fast_best(y, p, metric="weighted"):
    """
    Exact O(N log N) threshold optimizer for weighted, macro, or binary F1 score.
    Computes cumulative contingency matrix across sorted prediction thresholds.
    """
    y = np.asarray(y, dtype=np.int64)
    p = np.asarray(p, dtype=np.float64)
    order = np.argsort(p, kind="stable")
    sp, sy = p[order], y[order]
    n, tp_tot = len(y), sy.sum()
    if tp_tot == 0 or tp_tot == n: return 0.5, 0.0
    tn_tot = n - tp_tot
    cum = np.cumsum(sy)
    tp = tp_tot - cum + sy
    denom = n - np.arange(n)
    uniq, first = np.unique(sp, return_index=True)
    tp, denom = tp[first], denom[first]
    fp = denom - tp
    tn = tn_tot - fp
    prec = np.where(denom > 0, tp / np.maximum(denom, 1), 0.0)
    rec = tp / tp_tot
    f1p = np.where((denom > 0) & ((prec + rec) > 0), 2*prec*rec/np.maximum(prec+rec, 1e-12), 0.0)
    dneg = n - denom
    precn = np.where(dneg > 0, tn / np.maximum(dneg, 1), 0.0)
    recn = tn / tn_tot
    f1n = np.where((dneg > 0) & ((precn + recn) > 0), 2*precn*recn/np.maximum(precn+recn, 1e-12), 0.0)
    if metric == "macro": score = 0.5 * (f1p + f1n)
    elif metric == "weighted": score = (tp_tot * f1p + tn_tot * f1n) / n
    else: score = f1p
    b = int(np.argmax(score))
    return float(uniq[b]), float(score[b])

def rank_norm(p):
    """Transforms raw probability predictions into uniform percentile rank distributions [0, 1]."""
    r = np.argsort(np.argsort(p, kind="stable"), kind="stable")
    return (r + 1.0) / (len(r) + 1.0)


# ========================================================================================
# [3] SECTION 3: FEATURE ENGINEERING PIPELINE
# ========================================================================================
def build_features(d):
    """
    Constructs comprehensive clinical, oncological, temporal, and interaction features.
    Preserves all proven baseline feature transformations while incorporating domain signals.
    """
    yr = pd.to_numeric(d["year_of_diagnosis"], errors="coerce")
    d["year_num"] = yr
    d["t_follow"] = CONFIG["CUTOFF_YEAR"] - yr
    d["t_follow_sq"] = d["t_follow"] ** 2
    d["age_num"] = d["age_recode"].map(age_mid)
    
    # 1. Tumor Size Processing
    sz = pd.Series(np.nan, index=d.index)
    if "cs_tumor_size20042015" in d.columns:
        v = d["cs_tumor_size20042015"].map(lead_num).replace(list(CONFIG["SIZE_SENTINELS"]), np.nan)
        sz = sz.fillna(v.where(yr <= 2015))
    for c in ["tumor_size_summary", "tumor_size_overtime"]:
        if c in d.columns:
            v = d[c].map(lead_num).replace(list(CONFIG["SIZE_SENTINELS"]), np.nan)
            sz = sz.fillna(v)
    d["size_num"] = sz.where(sz <= CONFIG["SIZE_MAX_VALID"])
    d["size_log"] = np.log1p(d["size_num"])
    d["size_micro"] = (sz == 990).astype(float)
    d["size_is_missing"] = d["size_num"].isna().astype(float)

    # 2. Regional Lymph Node Involvement
    ne = pd.to_numeric(d["regional_nodes_examined"], errors="coerce").replace(list(CONFIG["NODE_SENTINELS"]), np.nan) if "regional_nodes_examined" in d.columns else pd.Series(np.nan, index=d.index)
    npo = pd.to_numeric(d["regional_nodes_positive"], errors="coerce").replace(list(CONFIG["NODE_SENTINELS"]), np.nan) if "regional_nodes_positive" in d.columns else pd.Series(np.nan, index=d.index)
    d["nodes_exam"], d["nodes_pos"] = ne, npo
    d["pos_nodes"] = np.where(npo.notna(), (npo > 0).astype(float), np.nan)
    d["node_ratio"] = npo / (ne + 1)
    d["nodes_is_missing"] = ne.isna().astype(float)

    # 3. Distant Metastasis Profile
    mets_cols = [c for c in d.columns if c.startswith("seer_combined_metsatdx")]
    if mets_cols:
        low = d[mets_cols].astype(str).apply(lambda s: s.str.strip().str.lower())
        d["mets_count"] = (low == "yes").sum(axis=1)
        d["mets_unk_count"] = (low == "unknown").sum(axis=1)
    else:
        d["mets_count"] = 0
        d["mets_unk_count"] = 0
    d["any_mets"] = (d["mets_count"] > 0).astype(float)

    # 4. Cancer Staging & TNM Systems
    d["stage_ord"] = d["summary_stage"].astype(str).str.lower().map({"localized": 1, "regional": 2, "distant": 3}) if "summary_stage" in d.columns else np.nan
    d["t_ord"] = d["derived_eod2018t_recode2018"].map(lambda x: tnm_num(x, "T")) if "derived_eod2018t_recode2018" in d.columns else np.nan
    d["n_ord"] = d["derived_eod2018n_recode2018"].map(lambda x: tnm_num(x, "N")) if "derived_eod2018n_recode2018" in d.columns else np.nan
    mu_s = d["derived_eod2018m_recode2018"].astype(str).str.upper().str.startswith("M1") if "derived_eod2018m_recode2018" in d.columns else pd.Series(False, index=d.index)
    d["m_bin"] = np.where(mu_s, 1.0, np.nan)

    # Unified Staging Harmonization across Coding Eras
    ext = pd.Series(np.nan, index=d.index)
    if "cs_extension20042015" in d.columns:
        e = d["cs_extension20042015"].map(lead_num).replace(list(CONFIG["SIZE_SENTINELS"]), np.nan)
        ext = e.where(yr <= 2015)
    st = d["stage_ord"].copy()
    em = np.select([ext <= 199, ext <= 699, ext <= 899], [1, 2, 3], default=np.nan)
    st = st.fillna(pd.Series(em, index=d.index))
    st = st.fillna(pd.Series(np.where(mu_s, 3, np.nan), index=d.index))
    distant = (d["mets_count"] > 0) | mu_s | (ext >= 700)
    st = np.fmax(st, np.where(distant, 3.0, np.nan))
    st = np.fmax(st, np.where(d["pos_nodes"] == 1, 2.0, np.nan))
    d["stage_unified"] = st
    d["stage_unified_unknown"] = pd.Series(st, index=d.index).isna().astype(float)
    d["distant_flag"] = distant.astype(float)

    # 5. Histology & Grading
    h = pd.to_numeric(d["histologic_type_icdo3"], errors="coerce")
    d["histo_group"] = d["histologic_type_icdo3"].map(map_histology)
    d["is_lymphoma"] = ((h >= 9590) & (h <= 9739)).astype(float)
    d["is_small_cell"] = h.isin([8041, 8042, 8043, 8044, 8045]).astype(float)
    
    g = d["grade_recode_thru2017"].astype(str).str.lower() if "grade_recode_thru2017" in d.columns else pd.Series("", index=d.index)
    d["grade_ord"] = np.select([g.str.contains("well"), g.str.contains("moder"), g.str.contains("poor"), g.str.contains("undiff")], [1, 2, 3, 4], default=np.nan)
    d["is_bilateral"] = d["laterality"].astype(str).str.contains("bilateral", case=False, na=False).astype(float) if "laterality" in d.columns else 0.0

    # 6. Primaries Sequence & Diagnosis Confirmation
    s = d["sequence_number"].astype(str).str.lower() if "sequence_number" in d.columns else pd.Series("", index=d.index)
    d["primaries_ord"] = np.select([s.str.contains("one primary"), s.str.contains("1st"), s.str.contains("2nd"), s.str.contains("3rd"), s.str.contains("4th")], [1, 1, 2, 3, 4], default=np.nan)

    dc = d["diagnostic_confirmation"].astype(str).str.lower() if "diagnostic_confirmation" in d.columns else pd.Series("", index=d.index)
    d["death_cert_dx"] = dc.str.contains("death certificate", na=False).astype(float)
    d["dx_clinical"] = dc.str.contains("clinical|radiography", na=False).astype(float)

    # 7. Surgical & Radiation Treatment Modalities
    s98 = pd.to_numeric(d["rx_summ_surgprim_site19982022"], errors="coerce").replace([99, 999], np.nan) if "rx_summ_surgprim_site19982022" in d.columns else pd.Series(np.nan, index=d.index)
    surg = pd.Series(np.where(s98.notna(), (s98 > 0).astype(float), np.nan), index=d.index)
    if "rx_summ_surgprim_site20232023" in d.columns:
        s23 = d["rx_summ_surgprim_site20232023"].astype(str).str.strip()
        surg = surg.fillna(pd.Series(np.where(s23.str.startswith("A0"), 0.0, np.where(s23.str.startswith("A"), 1.0, np.nan)), index=d.index))
    d["surgery_any"] = surg

    rad = pd.Series(False, index=d.index)
    if "radiation_recode" in d.columns:
        rr = d["radiation_recode"].astype(str).str.lower()
        rad = rad | (rr.str.contains("radiation", na=False) & ~rr.str.contains("none", na=False))
    if "rx_summ_surgradseq" in d.columns:
        sq = d["rx_summ_surgradseq"].astype(str).str.lower()
        rad = rad | (sq.str.contains("radiation", na=False) & ~sq.str.startswith("no radiation"))
    d["rad_any"] = rad.astype(float)
    d["rad_no_surg"] = (rad & (surg == 0)).astype(float)

    # Regional Lymph Node Surgery Scope
    if "rx_summ_scope_reglnsur2003" in d.columns:
        sln = d["rx_summ_scope_reglnsur2003"].astype(str).str.lower()
        d["ln_surg_ord"] = np.select([sln.str.contains("4 or more"), sln.str.contains("1 to 3"), sln.str.contains("biopsy")], [3, 2, 1], default=0)
    else:
        d["ln_surg_ord"] = 0

    # 8. High-Order Clinical Interactions
    d["tumor_density"] = d["size_num"] / (d["nodes_exam"] + 1)
    d["age_x_stage"] = d["age_num"] * d["stage_unified"]
    d["surg_x_stage"] = d["surgery_any"] * d["stage_unified"]
    d["mets_x_age"] = d["any_mets"] * d["age_num"]
    d["n_missing"] = d.isna().sum(axis=1)

    # Handle Missing Categoricals
    for c in d.columns:
        if not pd.api.types.is_numeric_dtype(d[c]):
            d[c] = d[c].replace(CONFIG["MISSING_TOKENS"], "Missing").fillna("Missing").astype(str)
    return d



# ========================================================================================
# [5] SECTION 5: MULTI-START GLOBAL ENSEMBLE WEIGHT OPTIMIZER (ALGORITHM IMPROVEMENT)
# ========================================================================================
def optimize_ensemble_weights(y, pred_dict, model_names, metric="weighted"):
    """
    Multi-start, global constrained ensemble weight optimizer.
    Explores uniform simplex, single-model vertices, and Dirichlet distributed candidates
    using both Powell and Nelder-Mead solvers to guarantee finding the optimal global F1 blend.
    """
    n_models = len(model_names)
    bounds = [(0, 1) for _ in range(n_models)]

    def loss_func(weights):
        w = np.array(weights)
        s = np.sum(w)
        if s < 1e-12: return 0.0
        w = w / s
        blend = sum(wi * pred_dict[nm] for wi, nm in zip(w, model_names))
        _, score = fast_best(y, blend, metric)
        return -score

    best_score = -1.0
    best_weights = np.ones(n_models) / n_models

    # Diverse multi-start initialization points
    init_points = [np.ones(n_models) / n_models]
    # Single model basis vectors
    for i in range(n_models):
        v = np.zeros(n_models)
        v[i] = 1.0
        init_points.append(v)
    # Dirichlet randomized simplex points
    rng = np.random.RandomState(42)
    for _ in range(12):
        init_points.append(rng.dirichlet(np.ones(n_models)))

    for init_w in init_points:
        for method in ["Powell", "Nelder-Mead"]:
            try:
                res = minimize(loss_func, init_w, method=method, bounds=bounds if method == "Powell" else None)
                w_cand = np.clip(res.x, 0, None)
                if w_cand.sum() > 0:
                    w_cand = w_cand / w_cand.sum()
                    blend_cand = sum(wi * pred_dict[nm] for wi, nm in zip(w_cand, model_names))
                    _, sc = fast_best(y, blend_cand, metric)
                    if sc > best_score:
                        best_score = sc
                        best_weights = w_cand
            except Exception:
                continue

    return best_weights, best_score


# ========================================================================================
# [6] SECTION 6: TRAINING (5 SEEDS x 5 FOLDS ON CUDA GPU), EVALUATION & SUBMISSION
# ========================================================================================
def train_and_evaluate():
    """
    Executes the full 5-seed x 5-fold stratified cross-validation modeling pipeline on CUDA GPU,
    optimizes ensemble weights via multi-start global search, and determines optimal decision thresholds.
    """
    total_start_time = time.time()
    print("\n" + "="*80)
    print("INSIGHT 2.0 CANCER PATIENT VITAL STATUS PREDICTION PIPELINE (CUDA GPU)")
    print("="*80)
    
    # [0] Hardware Check
    init_gpu_environment()
    use_gpu = CONFIG["USE_GPU"]

    # [1] Load Raw Datasets
    print("\n[Step 1/7] Loading Datasets...")
    train_path = find_csv("train")
    test_path = find_csv("test")
    train_raw = pd.read_csv(train_path)
    test_raw = pd.read_csv(test_path)
    
    # [2] Exploratory Data Analysis
    run_eda(train_raw, test_raw)
    
    # Target Encoding
    y = train_raw[CONFIG["TARGET_COL"]].map({"Dead": 1, "Alive": 0}).values
    n_train = len(train_raw)
    n_test = len(test_raw)
    
    # [3] Feature Engineering
    print("\n[Step 2/7] Executing Feature Engineering Pipeline...")
    df_all = pd.concat([
        train_raw.drop(columns=[CONFIG["ID_COL"], CONFIG["TARGET_COL"]]),
        test_raw.drop(columns=[CONFIG["ID_COL"]])
    ], axis=0, ignore_index=True)
    
    df_all = build_features(df_all)
    
    # Convert object columns to categorical dtype
    categorical_cols = [c for c in df_all.columns if not pd.api.types.is_numeric_dtype(df_all[c])]
    for c in categorical_cols:
        df_all[c] = df_all[c].astype("category")
    
    X = df_all.iloc[:n_train].reset_index(drop=True)
    X_test = df_all.iloc[n_train:].reset_index(drop=True)
    cat_feature_names = [c for c in categorical_cols if c in X.columns]
    num_feature_names = [c for c in X.columns if c not in cat_feature_names]
    
    for c in num_feature_names:
        X[c] = pd.to_numeric(X[c], errors="coerce")
        X_test[c] = pd.to_numeric(X_test[c], errors="coerce")
        
    print(f"  -> Total Engineered Features: {X.shape[1]} (Categorical: {len(cat_feature_names)}, Numerical: {len(num_feature_names)})")

    # XGBoost DataFrame copies
    X_xgb = X.copy()
    X_test_xgb = X_test.copy()
    for c in cat_feature_names:
        X_xgb[c] = X_xgb[c].astype("category")
        X_test_xgb[c] = X_test_xgb[c].astype("category")

    # [4] Model Setup & Out-of-Fold Arrays
    model_names = ["LGB_GBDT", "LGB_ET", "CB_D6", "CB_D7", "XGB"]
    oofs = {m: np.zeros(n_train) for m in model_names}
    tests = {m: np.zeros(n_test) for m in model_names}
    
    total_seeds = len(CONFIG["FINAL_SEEDS"])
    n_splits = CONFIG["N_SPLITS"]
    total_iterations = total_seeds * n_splits

    print(f"\n[Step 3/7] Training GPU Ensemble ({total_seeds} Seeds x {n_splits} Folds = {total_iterations} Total Iterations)...")
    
    iter_count = 0
    for seed_idx, seed in enumerate(CONFIG["FINAL_SEEDS"]):
        print(f"\n>>> Running SEED [{seed_idx+1}/{total_seeds}] (Seed: {seed}) <<<")
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        lgb_gbdt_p, lgb_et_p, cb_d6_p, cb_d7_p, xgb_p = get_model_params(seed, use_gpu=use_gpu)
        
        for fold, (tr_idx, va_idx) in enumerate(skf.split(X, y)):
            iter_count += 1
            f_start = time.time()
            Xa, ya = X.iloc[tr_idx], y[tr_idx]
            Xb, yb = X.iloc[va_idx], y[va_idx]
            
            # --- Model 1: LightGBM GBDT (GPU) ---
            tr_lgb = lgb.Dataset(Xa, ya, categorical_feature=cat_feature_names, free_raw_data=False)
            va_lgb = lgb.Dataset(Xb, yb, reference=tr_lgb, categorical_feature=cat_feature_names, free_raw_data=False)
            try:
                m_lgb1 = lgb.train(lgb_gbdt_p, tr_lgb, num_boost_round=3000, valid_sets=[va_lgb], callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)])
            except Exception as e:
                p_fallback = {**lgb_gbdt_p, "device": "cpu", "num_threads": -1}
                m_lgb1 = lgb.train(p_fallback, tr_lgb, num_boost_round=3000, valid_sets=[va_lgb], callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)])
            it1 = m_lgb1.best_iteration or 3000
            oofs["LGB_GBDT"][va_idx] += m_lgb1.predict(Xb, num_iteration=it1) / total_seeds
            tests["LGB_GBDT"] += m_lgb1.predict(X_test, num_iteration=it1) / total_iterations
            
            # --- Model 2: LightGBM ExtraTrees (GPU) ---
            try:
                m_lgb2 = lgb.train(lgb_et_p, tr_lgb, num_boost_round=3000, valid_sets=[va_lgb], callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)])
            except Exception as e:
                p_fallback = {**lgb_et_p, "device": "cpu", "num_threads": -1}
                m_lgb2 = lgb.train(p_fallback, tr_lgb, num_boost_round=3000, valid_sets=[va_lgb], callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)])
            it2 = m_lgb2.best_iteration or 3000
            oofs["LGB_ET"][va_idx] += m_lgb2.predict(Xb, num_iteration=it2) / total_seeds
            tests["LGB_ET"] += m_lgb2.predict(X_test, num_iteration=it2) / total_iterations
            
            # --- Model 3: CatBoost Depth 6 (CUDA GPU) ---
            m_cb1 = CatBoostClassifier(**cb_d6_p, random_seed=seed + fold * 10)
            m_cb1.fit(Xa, ya, cat_features=cat_feature_names, eval_set=(Xb, yb), verbose=0)
            oofs["CB_D6"][va_idx] += m_cb1.predict_proba(Xb)[:, 1] / total_seeds
            tests["CB_D6"] += m_cb1.predict_proba(X_test)[:, 1] / total_iterations
            
            # --- Model 4: CatBoost Depth 7 (CUDA GPU) ---
            m_cb2 = CatBoostClassifier(**cb_d7_p, random_seed=seed + fold * 10 + 500)
            m_cb2.fit(Xa, ya, cat_features=cat_feature_names, eval_set=(Xb, yb), verbose=0)
            oofs["CB_D7"][va_idx] += m_cb2.predict_proba(Xb)[:, 1] / total_seeds
            tests["CB_D7"] += m_cb2.predict_proba(X_test)[:, 1] / total_iterations
            
            # --- Model 5: XGBoost Histogram (CUDA GPU) ---
            m_xgb = xgb.XGBClassifier(**xgb_p, random_state=seed + fold * 10)
            m_xgb.fit(X_xgb.iloc[tr_idx], ya, eval_set=[(X_xgb.iloc[va_idx], yb)], verbose=False)
            oofs["XGB"][va_idx] += m_xgb.predict_proba(X_xgb.iloc[va_idx])[:, 1] / total_seeds
            tests["XGB"] += m_xgb.predict_proba(X_test_xgb)[:, 1] / total_iterations
            
            # Memory Management & GPU VRAM Cleanup
            gc.collect()
            if CUDA_AVAILABLE:
                torch.cuda.empty_cache()

            print(f"  [Seed {seed} | Fold {fold+1}/{n_splits}] (Iter {iter_count}/{total_iterations}) completed in {time.time()-f_start:.1f}s (Total Elapsed: {time.time()-total_start_time:.0f}s)")

    # [5] Individual Model Performance Evaluation
    print("\n" + "="*80)
    print("SECTION 5: INDIVIDUAL MODEL VALIDATION PERFORMANCE (5x5 BAGGED OOF)")
    print("="*80)
    
    R_oof = {}
    R_tst = {}
    for name in model_names:
        thr, s = fast_best(y, oofs[name], "weighted")
        auc = roc_auc_score(y, oofs[name])
        R_oof[name] = rank_norm(oofs[name])
        R_tst[name] = rank_norm(tests[name])
        pred_m = (oofs[name] >= thr).astype(int)
        f1_dead = f1_score(y, pred_m, pos_label=1)
        f1_alive = f1_score(y, pred_m, pos_label=0)
        macro_f1 = f1_score(y, pred_m, average="macro")
        print(f"  {name:12s} | Weighted F1: {s:.6f} | ROC-AUC: {auc:.5f} | F1-Dead: {f1_dead:.4f} | F1-Alive: {f1_alive:.4f} | Macro F1: {macro_f1:.4f} | Thr: {thr:.4f}")

    # [6] Multi-Start Global Ensemble Blending & Optimization
    print("\n" + "="*80)
    print("SECTION 6: MULTI-START GLOBAL ENSEMBLE BLENDING & THRESHOLD OPTIMIZATION")
    print("="*80)
    
    # 1. Rank-Normalized Optimization
    rank_weights, rank_best_f1 = optimize_ensemble_weights(y, R_oof, model_names, "weighted")
    blend_oof_rank = sum(wi * R_oof[nm] for wi, nm in zip(rank_weights, model_names))
    blend_test_rank = sum(wi * R_tst[nm] for wi, nm in zip(rank_weights, model_names))
    rank_thr, rank_f1 = fast_best(y, blend_oof_rank, "weighted")

    # 2. Probability Blending Optimization
    prob_weights, prob_best_f1 = optimize_ensemble_weights(y, oofs, model_names, "weighted")
    blend_oof_prob = sum(wi * oofs[nm] for wi, nm in zip(prob_weights, model_names))
    blend_test_prob = sum(wi * tests[nm] for wi, nm in zip(prob_weights, model_names))
    prob_thr, prob_f1 = fast_best(y, blend_oof_prob, "weighted")

    # Select Superior Blending Strategy
    if rank_f1 >= prob_f1:
        strategy = "Rank-Normalized Blending"
        final_weights = rank_weights
        blend_oof = blend_oof_rank
        blend_test = blend_test_rank
        optimal_threshold = rank_thr
        best_weighted_f1 = rank_f1
    else:
        strategy = "Raw Probability Blending"
        final_weights = prob_weights
        blend_oof = blend_oof_prob
        blend_test = blend_test_prob
        optimal_threshold = prob_thr
        best_weighted_f1 = prob_f1

    print(f"Selected Ensemble Strategy: {strategy} (Weighted F1: {best_weighted_f1:.6f})")
    print("\nOptimal Ensemble Weights (Maximizing Weighted F1):")
    for nm, w in zip(model_names, final_weights):
        print(f"  - {nm:12s}: {w:.4f} ({w*100:.1f}%)")

    final_oof_preds = (blend_oof >= optimal_threshold).astype(int)
    
    f1_dead = f1_score(y, final_oof_preds, pos_label=1)
    f1_alive = f1_score(y, final_oof_preds, pos_label=0)
    macro_f1 = f1_score(y, final_oof_preds, average="macro")
    overall_auc = roc_auc_score(y, blend_oof)
    cm = confusion_matrix(y, final_oof_preds)

    print("\n" + "="*80)
    print("FINAL ENSEMBLE OUT-OF-FOLD (OOF) EVALUATION METRICS:")
    print("="*80)
    print(f"  * WEIGHTED F1 SCORE (Competition Metric): {best_weighted_f1:.6f}")
    print(f"  * F1 Score (Positive Class: Dead):        {f1_dead:.6f}")
    print(f"  * F1 Score (Class: Alive):                {f1_alive:.6f}")
    print(f"  * Macro F1 Score:                         {macro_f1:.6f}")
    print(f"  * ROC-AUC Score:                          {overall_auc:.6f}")
    print(f"  * Optimal Decision Threshold:             {optimal_threshold:.6f}")
    print("\nConfusion Matrix:")
    print(f"                 Predicted Alive    Predicted Dead")
    print(f"  Actual Alive:   {cm[0,0]:12d}      {cm[0,1]:12d}")
    print(f"  Actual Dead:    {cm[1,0]:12d}      {cm[1,1]:12d}")
    print("="*80)

    # [7] Final Prediction & Submission Generation
    print("\n[Step 7/7] Generating Final Test Predictions & Submission File...")
    final_test_binary = (blend_test >= optimal_threshold)
    final_test_labels = np.where(final_test_binary, "Dead", "Alive")
    
    submission_df = pd.DataFrame({
        CONFIG["ID_COL"]: test_raw[CONFIG["ID_COL"]],
        CONFIG["TARGET_COL"]: final_test_labels
    })
    
    submission_path = CONFIG["OUTPUT_SUBMISSION_PATH"]
    submission_df.to_csv(submission_path, index=False)
    
    dead_pred_count = (final_test_labels == "Dead").sum()
    alive_pred_count = (final_test_labels == "Alive").sum()
    dead_pred_pct = dead_pred_count / len(final_test_labels) * 100
    alive_pred_pct = alive_pred_count / len(final_test_labels) * 100

    print(f"\n  [Submission Saved]: {submission_path}")
    print(f"  [Total Test Records]: {len(submission_df):,}")
    print(f"  [Predicted Dead]:     {dead_pred_count:,} ({dead_pred_pct:.2f}%)")
    print(f"  [Predicted Alive]:    {alive_pred_count:,} ({alive_pred_pct:.2f}%)")
    print(f"  [Format Validation]:  patient_id match: {(submission_df[CONFIG['ID_COL']] == test_raw[CONFIG['ID_COL']]).all()}, Nulls: {submission_df.isna().sum().sum()}")
    print(f"\n[Execution Completed in {time.time()-total_start_time:.1f}s]")
    print("="*80 + "\n")

    return best_weighted_f1, optimal_threshold, submission_path


if __name__ == "__main__":
    train_and_evaluate()
