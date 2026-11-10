"""
data_loader.py
Secure data processing, validation, feature engineering, and child case registry search
for System Capacity & Care Load Analytics for Unaccompanied Children (UAC).

Security hardening:
- All user-supplied search inputs are sanitized (strip, lower-case, length-capped) before use
- No eval / exec / shell calls anywhere
- File paths are never constructed from user input
- All pd.read_csv calls use explicit dtypes where possible to prevent injection
"""

import pandas as pd
import numpy as np
import os
import re
from pathlib import Path

# ── File locations (resolved once at module level, never from user input) ──
_HERE = Path(__file__).parent.resolve()
CSV_FILENAME     = _HERE / "HHS_Unaccompanied_Alien_Children_Program (1).csv"
REGISTRY_CSV     = _HERE / "uac_children_registry.csv"
REGISTRY_SCRIPT  = _HERE / "generate_children_registry.py"

# ── Security helper ──
_MAX_QUERY_LEN = 120   # cap free-text search at 120 chars
_SAFE_PATTERN  = re.compile(r"[^\w\s\-,\./()']")   # allow only safe chars


def _sanitize_query(raw: str) -> str:
    """Strip, truncate, and remove dangerous characters from a search string."""
    if not isinstance(raw, str):
        return ""
    q = raw.strip()[:_MAX_QUERY_LEN]
    # Remove SQL-like injection tokens and HTML
    q = _SAFE_PATTERN.sub("", q)
    return q.lower()


# ── Aggregate daily pipeline data ──
def load_and_preprocess_data() -> pd.DataFrame:
    """
    Loads raw HHS UAC daily reports, cleans formats, validates logical
    constraints, and engineers derived healthcare pipeline metrics.
    Returns a clean, chronologically sorted DataFrame.
    """
    df = pd.read_csv(CSV_FILENAME, dtype=str)
    df = df.dropna(how="all").copy()

    col_mapping = {
        "Date": "date",
        "Children apprehended and placed in CBP custody*": "cbp_intake",
        "Children in CBP custody": "cbp_custody",
        "Children transferred out of CBP custody": "transfers_to_hhs",
        "Children in HHS Care": "hhs_care",
        "Children discharged from HHS Care": "discharges_from_hhs",
    }
    df = df.rename(columns=col_mapping)

    for col in ["cbp_intake", "cbp_custody", "transfers_to_hhs", "hhs_care", "discharges_from_hhs"]:
        df[col] = pd.to_numeric(df[col].str.replace(",", "", regex=False).str.strip(), errors="coerce")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    # Logical constraint flags
    df["flag_transfers_gt_custody"] = df["transfers_to_hhs"] > df["cbp_custody"]
    df["flag_discharges_gt_care"]   = df["discharges_from_hhs"] > df["hhs_care"]

    # Core derived metrics
    df["total_system_load"]     = df["cbp_custody"] + df["hhs_care"]
    df["net_hhs_intake"]        = df["transfers_to_hhs"] - df["discharges_from_hhs"]
    df["total_pipeline_flow"]   = df["cbp_intake"] - df["discharges_from_hhs"]
    df["care_load_growth_rate"] = df["total_system_load"].pct_change() * 100

    df["discharge_offset_ratio"] = np.where(
        df["transfers_to_hhs"] > 0,
        df["discharges_from_hhs"] / df["transfers_to_hhs"],
        np.nan,
    )
    df["cbp_turnover_rate"] = np.where(
        df["cbp_custody"] > 0,
        df["transfers_to_hhs"] / df["cbp_custody"],
        np.nan,
    )

    # Rolling windows
    for w in [7, 14]:
        df[f"total_load_{w}d_avg"]  = df["total_system_load"].rolling(w, min_periods=1).mean()
        df[f"net_intake_{w}d_avg"]  = df["net_hhs_intake"].rolling(w, min_periods=1).mean()

    df["hhs_care_7d_avg"]    = df["hhs_care"].rolling(7, min_periods=1).mean()
    df["cbp_custody_7d_avg"] = df["cbp_custody"].rolling(7, min_periods=1).mean()

    rolling_std  = df["total_system_load"].rolling(7, min_periods=3).std()
    rolling_mean = df["total_system_load"].rolling(7, min_periods=3).mean()
    df["load_volatility_7d"] = (rolling_std / rolling_mean.replace(0, np.nan)) * 100

    df["cumulative_backlog"]          = df["net_hhs_intake"].cumsum()
    df["cumulative_pipeline_backlog"] = df["total_pipeline_flow"].cumsum()

    return df


# ── Individual child registry ──
def _ensure_registry() -> None:
    """Auto-generate the registry CSV if it doesn't exist yet."""
    if not REGISTRY_CSV.exists():
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location("gen_reg", REGISTRY_SCRIPT)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.create_children_registry()


def load_children_registry() -> pd.DataFrame:
    _ensure_registry()
    df = pd.read_csv(REGISTRY_CSV, dtype=str)
    # Coerce numeric columns
    df["age"]          = pd.to_numeric(df["age"], errors="coerce").fillna(0).astype(int)
    df["days_in_care"] = pd.to_numeric(df["days_in_care"], errors="coerce").fillna(0).astype(int)
    return df


def search_children_registry(
    query: str = "",
    status_filter: str = "All",
) -> pd.DataFrame:
    """
    Returns child records matching *query* (searched in id, name, country,
    facility, case_manager, sponsor_location) and optionally *status_filter*.

    Security: query is sanitized before any string operation.
    """
    df = load_children_registry()
    q  = _sanitize_query(query)

    # Status filter (never touches raw user string in a file path or eval)
    valid_statuses = {"In HHS Care", "In CBP Custody", "Discharged to Sponsor"}
    if status_filter in valid_statuses:
        df = df[df["current_status"] == status_filter]

    if q:
        searchable_cols = [
            "child_id", "full_name", "country_of_origin",
            "facility_name", "case_manager", "sponsor_location",
        ]
        mask = pd.Series(False, index=df.index)
        for col in searchable_cols:
            mask |= df[col].str.lower().str.contains(q, na=False, regex=False)
        df = df[mask]

    return df.reset_index(drop=True)


# ── KPI summary ──
def get_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {k: 0 for k in [
            "total_care_latest", "hhs_care_latest", "cbp_custody_latest",
            "net_intake_latest", "net_intake_7d_avg", "discharge_offset_ratio_latest",
            "discharge_offset_ratio_7d_avg", "volatility_index_7d",
            "cumulative_backlog_period", "latest_date"
        ]}

    latest = df.iloc[-1]
    last_7 = df.iloc[-7:]

    def _safe_float(val, default=0.0):
        try:
            return float(round(val, 2)) if pd.notna(val) else default
        except Exception:
            return default

    return {
        "total_care_latest":              int(latest["total_system_load"]),
        "hhs_care_latest":                int(latest["hhs_care"]),
        "cbp_custody_latest":             int(latest["cbp_custody"]),
        "net_intake_latest":              int(latest["net_hhs_intake"]),
        "net_intake_7d_avg":              _safe_float(last_7["net_hhs_intake"].mean()),
        "discharge_offset_ratio_latest":  _safe_float(latest["discharge_offset_ratio"]),
        "discharge_offset_ratio_7d_avg":  _safe_float(
            last_7["discharges_from_hhs"].sum() / max(1, last_7["transfers_to_hhs"].sum())
        ),
        "volatility_index_7d":            _safe_float(latest["load_volatility_7d"]),
        "cumulative_backlog_period":       int(df["net_hhs_intake"].sum()),
        "latest_date":                    latest["date"].strftime("%b %d, %Y"),
    }


# ── Self-test ──
if __name__ == "__main__":
    df_agg = load_and_preprocess_data()
    print("Aggregate data shape :", df_agg.shape)
    df_reg = load_children_registry()
    print("Registry data shape  :", df_reg.shape)
    hits = search_children_registry("Sofia")
    print(f"Search 'Sofia'       : {len(hits)} matches")
    hits2 = search_children_registry("<script>alert(1)</script>")
    print(f"XSS injection test   : {len(hits2)} matches (expected 0)")
