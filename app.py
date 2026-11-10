"""
app.py – System Capacity & Care Load Analytics for Unaccompanied Children (UAC)
Spotify-Themed Modern 3D Black Glassmorphic Executive Dashboard
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta

from data_loader import (
    get_kpis,
    load_and_preprocess_data,
    load_children_registry,
    search_children_registry,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UAC System Capacity & Care Load Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS: Spotify Black & Neon Green Theme (rendered via st.html) ────────
css_styles = """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], .stApp {
  background-color: #000000 !important;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: #FFFFFF !important;
}

.block-container {
  padding-top: 1rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 1420px !important;
}

header[data-testid="stHeader"] {
  display: none !important;
}

/* ─ Modern Spotify-Inspired Navbar ─ */
.top-nav {
  background: linear-gradient(135deg, #121212 0%, #181818 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: 2px solid rgba(30, 215, 96, 0.4);
  border-radius: 20px;
  padding: 16px 24px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(30, 215, 96, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 18px;
}

/* ─ 3D Glowing Logo Container ─ */
.nav-logo-3d {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, #0A4D22 0%, #121212 100%);
  border: 1px solid rgba(30, 215, 96, 0.5);
  box-shadow: 0 10px 25px rgba(30, 215, 96, 0.35), inset 0 2px 4px rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ─ Spotify Neon Green Heading ─ */
.nav-title {
  font-size: 1.65rem;
  font-weight: 900;
  color: #1ED760 !important;
  letter-spacing: -0.025em;
  line-height: 1.15;
  text-shadow: 0 0 25px rgba(30, 215, 96, 0.45), 0 2px 4px rgba(0, 0, 0, 0.9);
}

.nav-sub {
  font-size: 0.82rem;
  color: #B3B3B3;
  margin-top: 3px;
  font-weight: 500;
}

.live-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(30, 215, 96, 0.12);
  border: 1px solid rgba(30, 215, 96, 0.4);
  color: #1ED760;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 9999px;
  white-space: nowrap;
  box-shadow: 0 0 15px rgba(30, 215, 96, 0.2);
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1ED760;
  box-shadow: 0 0 10px #1ED760;
}

/* ─ 4 Vibrant 3D KPI Cards ─ */
.kpi-card {
  border-radius: 20px;
  padding: 20px 22px 14px;
  position: relative;
  overflow: hidden;
  min-height: 148px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.kpi-card:hover {
  transform: translateY(-4px);
}
.kpi-purple {
  background: linear-gradient(135deg, #4C1D95 0%, #6D28D9 50%, #8B5CF6 100%);
  box-shadow: 0 14px 32px rgba(109, 40, 217, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.kpi-cyan {
  background: linear-gradient(135deg, #0369A1 0%, #0284C7 50%, #06B6D4 100%);
  box-shadow: 0 14px 32px rgba(6, 182, 212, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.kpi-peach {
  background: linear-gradient(135deg, #9A3412 0%, #C2410C 50%, #EA580C 100%);
  box-shadow: 0 14px 32px rgba(234, 88, 12, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.kpi-spotify {
  background: linear-gradient(135deg, #065F46 0%, #059669 45%, #10B981 100%);
  box-shadow: 0 14px 32px rgba(16, 185, 129, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.28);
}
.kpi-num {
  font-size: 2.15rem;
  font-weight: 800;
  color: #FFFFFF;
  line-height: 1.1;
  letter-spacing: -0.025em;
}
.kpi-lbl {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
  margin-top: 3px;
}
.kpi-det {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 2px;
}

/* ─ Spotify Black Glass Panels ─ */
.glass {
  background: #121212;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px 22px;
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  margin-bottom: 1rem;
}
.g-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
}
.g-sub {
  font-size: 0.77rem;
  color: #A7A7A7;
  margin-top: 2px;
}

/* ─ Child Dossier ─ */
.dossier {
  background: linear-gradient(135deg, #121212 0%, #1A1A1A 100%);
  border: 1px solid rgba(30, 215, 96, 0.5);
  border-radius: 18px;
  padding: 18px 24px;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.8), 0 0 25px rgba(30, 215, 96, 0.18);
  margin-bottom: 1.2rem;
}
.dos-name {
  font-size: 1.35rem;
  font-weight: 800;
  color: #FFFFFF;
}
.dos-id {
  background: rgba(30, 215, 96, 0.15);
  border: 1px solid #1ED760;
  color: #1ED760;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 700;
}
.dos-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 14px;
}
.dos-lbl {
  font-size: 0.7rem;
  color: #A7A7A7;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}
.dos-val {
  font-size: 0.95rem;
  font-weight: 700;
  color: #F8FAFC;
  margin-top: 2px;
}

/* ─ Inputs Dark Theme ─ */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
  background-color: #181818 !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  border-radius: 12px !important;
  color: #FFFFFF !important;
}
div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {
  border-color: #1ED760 !important;
  box-shadow: 0 0 12px rgba(30, 215, 96, 0.35) !important;
}
.stTextInput input {
  color: #FFFFFF !important;
  font-size: 0.9rem !important;
}

/* ─ Spotify Signature Green Button ─ */
.stButton > button, div[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, #1DB954 0%, #1ED760 100%) !important;
  color: #000000 !important;
  font-weight: 800 !important;
  font-size: 0.88rem !important;
  border: none !important;
  border-radius: 9999px !important;
  padding: 8px 22px !important;
  box-shadow: 0 4px 20px rgba(30, 215, 96, 0.45) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
  transform: scale(1.04) translateY(-2px) !important;
  box-shadow: 0 8px 30px rgba(30, 215, 96, 0.7) !important;
  color: #000000 !important;
}

/* ─ Dataframe ─ */
[data-testid="stDataFrame"] {
  border-radius: 14px !important;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
</style>"""
st.html(css_styles)

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_aggregate() -> pd.DataFrame:
    return load_and_preprocess_data()

@st.cache_data(show_spinner=False)
def _load_registry() -> pd.DataFrame:
    return load_children_registry()

df_raw = _load_aggregate()
df_registry = _load_registry()

# ── Session State Initializations & Safe Callbacks ─────────────────────────────
DEFAULT_CHILD_CHOICE = "All Registered Children (1,200 Cases)"

if "active_search_query" not in st.session_state:
    st.session_state["active_search_query"] = ""

def on_child_dropdown_change():
    chosen = st.session_state["child_dropdown_widget"]
    if chosen == DEFAULT_CHILD_CHOICE:
        st.session_state["active_search_query"] = ""
        st.session_state["keyword_search_widget"] = ""
    else:
        cid = chosen.split(" · ")[0].strip()
        st.session_state["active_search_query"] = cid
        st.session_state["keyword_search_widget"] = cid

def on_keyword_search_change():
    val = st.session_state["keyword_search_widget"].strip()
    st.session_state["active_search_query"] = val
    if not val:
        st.session_state["child_dropdown_widget"] = DEFAULT_CHILD_CHOICE

def on_reset_click():
    st.session_state["active_search_query"] = ""
    st.session_state["keyword_search_widget"] = ""
    st.session_state["child_dropdown_widget"] = DEFAULT_CHILD_CHOICE

# ── 3D Navbar HTML (rendered via st.html to prevent any markdown code leaks) ──
navbar_html = """<div class="top-nav"><div class="nav-left"><div class="nav-logo-3d"><svg width="42" height="42" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="sphere3d" cx="30%" cy="25%" r="70%"><stop offset="0%" stop-color="#72FF9C"/><stop offset="35%" stop-color="#1ED760"/><stop offset="70%" stop-color="#108439"/><stop offset="100%" stop-color="#042F12"/></radialGradient><filter id="shadow3d" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000000" flood-opacity="0.8"/></filter></defs><circle cx="24" cy="24" r="21" fill="url(#sphere3d)"/><ellipse cx="18" cy="13" rx="10" ry="5.5" fill="#FFFFFF" fill-opacity="0.45" transform="rotate(-25 18 13)"/><path d="M12 18.5C18 15.5 28 16 35 20.5" stroke="#04260E" stroke-width="3.6" stroke-linecap="round"/><path d="M12 17.5C18 14.5 28 15 35 19.5" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" filter="url(#shadow3d)"/><path d="M14 24.5C19 22 27 22.5 33 26.5" stroke="#04260E" stroke-width="3.6" stroke-linecap="round"/><path d="M14 23.5C19 21 27 21.5 33 25.5" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" filter="url(#shadow3d)"/><path d="M16 30.5C20.5 28.5 26 29 31 32.5" stroke="#04260E" stroke-width="3.6" stroke-linecap="round"/><path d="M16 29.5C20.5 27.5 26 28 31 31.5" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" filter="url(#shadow3d)"/></svg></div><div><div class="nav-title">System Capacity &amp; Care Load Analytics</div><div class="nav-sub">Unaccompanied Children (UAC) Healthcare Pipeline &nbsp;•&nbsp; CBP Intake &rarr; HHS Care &rarr; Sponsor Reunification</div></div></div><div class="live-pill"><span class="live-dot"></span> Active Pipeline Telemetry</div></div>"""
st.html(navbar_html)

# ── TOP CONTROL ROW: Child Search Dropdown + Text Input + Year/Month/Week/Day Time Filter ──
child_dropdown_options = [DEFAULT_CHILD_CHOICE] + [
    f"{r['child_id']} · {r['full_name']} ({r['current_status']})"
    for _, r in df_registry.iterrows()
]

ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5 = st.columns([2.6, 2.0, 1.8, 2.2, 1.4])

with ctrl_c1:
    # Child direct select dropdown (as in User Pic 1)
    st.selectbox(
        "Select Specific Child",
        options=child_dropdown_options,
        key="child_dropdown_widget",
        on_change=on_child_dropdown_change,
        label_visibility="collapsed",
    )

with ctrl_c2:
    # Optional keyword text search
    st.text_input(
        "Keyword Search",
        placeholder="🔍 Type Name, ID, Shelter...",
        key="keyword_search_widget",
        on_change=on_keyword_search_change,
        label_visibility="collapsed",
    )

with ctrl_c3:
    time_dimension = st.selectbox(
        "Time Dimension",
        ["📅 Year-Wise", "📆 Month-Wise", "📊 Week-Wise", "⏱️ Day-Wise"],
        index=0,
        label_visibility="collapsed",
    )

with ctrl_c4:
    # Build dynamic secondary period dropdown based on chosen dimension (as in User Pic 3)
    if time_dimension == "📅 Year-Wise":
        period_choice = st.selectbox(
            "Period",
            [
                "All-Time History (2023 – 2025)",
                "Year 2025 – Low Load & Contraction",
                "Year 2024 – Peak Intake Surge",
                "Year 2023 – Decompression Phase",
            ],
            index=0,
            label_visibility="collapsed",
        )
    elif time_dimension == "📆 Month-Wise":
        all_months = ["All Months (2023 – 2025 Aggregated)"] + [
            dt.strftime("%B %Y") for dt in pd.date_range("2023-01-01", "2025-12-31", freq="MS")[::-1]
        ]
        period_choice = st.selectbox("Period", all_months, index=0, label_visibility="collapsed")
    elif time_dimension == "📊 Week-Wise":
        period_choice = st.selectbox(
            "Period",
            [
                "All Weeks (Aggregated Full History)",
                "Last 4 Weeks",
                "Last 8 Weeks",
                "Last 12 Weeks",
                "Last 26 Weeks",
                "Last 52 Weeks",
            ],
            index=0,
            label_visibility="collapsed",
        )
    else:  # Day-Wise
        period_choice = st.selectbox(
            "Period",
            [
                "All Days (Daily Operational Resolution)",
                "Last 7 Days",
                "Last 14 Days",
                "Last 30 Days",
                "Last 60 Days",
                "Last 90 Days",
            ],
            index=0,
            label_visibility="collapsed",
        )

with ctrl_c5:
    export_slot = st.empty()

# ── Dynamic Slicing of Aggregate Data by Selected Year / Month / Week / Day ───
max_dt = df_raw["date"].max()
min_dt = df_raw["date"].min()

if time_dimension == "📅 Year-Wise":
    if "2025" in period_choice:
        df = df_raw[df_raw["date"].dt.year == 2025].copy()
    elif "2024" in period_choice:
        df = df_raw[df_raw["date"].dt.year == 2024].copy()
    elif "2023" in period_choice:
        df = df_raw[df_raw["date"].dt.year == 2023].copy()
    else:
        df = df_raw.copy()

elif time_dimension == "📆 Month-Wise":
    if period_choice == "All Months (2023 – 2025 Aggregated)":
        df = df_raw.copy()
    else:
        chosen_dt = datetime.strptime(period_choice, "%B %Y")
        df = df_raw[
            (df_raw["date"].dt.year == chosen_dt.year)
            & (df_raw["date"].dt.month == chosen_dt.month)
        ].copy()

elif time_dimension == "📊 Week-Wise":
    if "Last 4 Weeks" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(weeks=4))].copy()
    elif "Last 8 Weeks" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(weeks=8))].copy()
    elif "Last 12 Weeks" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(weeks=12))].copy()
    elif "Last 26 Weeks" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(weeks=26))].copy()
    elif "Last 52 Weeks" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(weeks=52))].copy()
    else:
        df = df_raw.copy()

else:  # Day-Wise
    if "Last 7 Days" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(days=7))].copy()
    elif "Last 14 Days" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(days=14))].copy()
    elif "Last 30 Days" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(days=30))].copy()
    elif "Last 60 Days" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(days=60))].copy()
    elif "Last 90 Days" in period_choice:
        df = df_raw[df_raw["date"] >= (max_dt - timedelta(days=90))].copy()
    else:
        df = df_raw.copy()

# Ensure df is not empty
if df.empty:
    df = df_raw.copy()

# Export Button in Toolbar
with export_slot:
    export_slot.download_button(
        "📊 Export CSV",
        data=df.to_csv(index=False).encode(),
        file_name=f"uac_data_{time_dimension[:2]}_{period_choice[:12].replace(' ','_')}.csv",
        mime="text/csv",
    )

# ── Execute Child Search (Isolated vs All Data Mode) ───────────────────────────
matched = search_children_registry(st.session_state["active_search_query"], status_filter="All")
is_single_child = (len(matched) == 1 and bool(st.session_state["active_search_query"].strip()))
is_filtered_search = bool(st.session_state["active_search_query"].strip())

# Compute Period-Level Healthcare KPIs
sys_kpis = get_kpis(df)
period_discharges = int(df["discharges_from_hhs"].sum())
period_transfers = int(df["transfers_to_hhs"].sum())
period_dor = period_discharges / max(1, period_transfers)
period_net_flow = int(df["net_hhs_intake"].sum())

# ── Dynamic Top 4 KPI Cards ────────────────────────────────────────────────────
# When user searches a specific child: show ONLY that child's info
# When not searching: show aggregate healthcare KPIs matching the selected Time Filter
if is_single_child:
    c = matched.iloc[0]
    kpi = [
        (c["current_status"], "Child Pipeline Status", f"Facility: {c['facility_name'][:40]}"),
        (f"{c['days_in_care']} Days", "Days in Active Care", f"Admitted: {c['admission_date']}"),
        (c["medical_status"][:22], "Medical Screening", c["medical_status"]),
        (c["sponsor_relation"], "Sponsor Placement", f"{c['sponsor_location']} · {c['sponsor_vetting_status'][:24]}"),
    ]
elif is_filtered_search:
    n = len(matched)
    hhs_n = int((matched["current_status"] == "In HHS Care").sum())
    dis_n = int((matched["current_status"] == "Discharged to Sponsor").sum())
    avg_los = float(matched["days_in_care"].mean()) if n else 0.0
    kpi = [
        (f"{n:,}", "Matching Child Records", f"Query: '{st.session_state['active_search_query']}'"),
        (f"{hhs_n:,}", "In Active HHS Care", f"{hhs_n/max(1,n)*100:.1f}% of cohort"),
        (f"{avg_los:.1f}d", "Avg Length of Stay", "Average duration in care"),
        (f"{dis_n:,}", "Reunified with Sponsors", f"{dis_n/max(1,n)*100:.1f}% placement rate"),
    ]
else:
    # Dynamically reflect the selected period (Year / Month / Week / Day)
    kpi = [
        (
            f"{sys_kpis['total_care_latest']:,}",
            "Total Under Care",
            f"HHS: {sys_kpis['hhs_care_latest']:,} | CBP: {sys_kpis['cbp_custody_latest']:,}",
        ),
        (
            f"{sys_kpis['hhs_care_latest']:,}",
            "Active in HHS Care",
            f"Period Net Flow: {period_net_flow:+d} ({df['net_hhs_intake'].mean():+.1f}/d)",
        ),
        (
            f"{period_dor:.2f}x",
            "Discharge Clearing Ratio",
            f"Period: {period_discharges:,} Discharged / {period_transfers:,} In",
        ),
        (
            f"{sys_kpis['volatility_index_7d']:.2f}%",
            "Care Volatility Index",
            f"Timeframe: {period_choice[:25]}",
        ),
    ]

# ── Dynamic SVG Sparklines for Top Cards ──────────────────────────────────────
def _sparkline(vals: list) -> str:
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = max(1e-9, hi - lo)
    W, H = 280, 48
    step = W / (len(vals) - 1)
    pts = [(i * step, H - 6 - ((v - lo) / rng) * (H - 14)) for i, v in enumerate(vals)]
    path = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        cx = x0 + (x1 - x0) / 2
        path += f" C {cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    return (
        f'<svg style="position:absolute;bottom:0;left:0;width:100%;height:48px;pointer-events:none"'
        f' viewBox="0 0 {W} {H}" preserveAspectRatio="none">'
        f'<path d="{path}" fill="none" stroke="rgba(0,0,0,.45)" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="{path}" fill="none" stroke="#FFF" stroke-width="2.6" stroke-linecap="round"/>'
        f'</svg>'
    )

tail_df = df.tail(min(len(df), 24))
sparks = [
    _sparkline(tail_df["total_system_load"].tolist()),
    _sparkline(tail_df["hhs_care"].tolist()),
    _sparkline(tail_df["discharge_offset_ratio"].fillna(1).clip(0, 4).tolist()),
    _sparkline(tail_df["cbp_intake"].tolist()),
]
card_colors = ["kpi-purple", "kpi-cyan", "kpi-peach", "kpi-spotify"]

# ── Render Row 1: KPI Cards ────────────────────────────────────────────────────
st.html("<div style='height:8px'></div>")
kpi_cols = st.columns(4)
for col, (num, lbl, det), spk, cls in zip(kpi_cols, kpi, sparks, card_colors):
    with col:
        st.html(
            f'<div class="kpi-card {cls}">'
            f'  <div>'
            f'    <div class="kpi-num">{num}</div>'
            f'    <div class="kpi-lbl">{lbl}</div>'
            f'    <div class="kpi-det">{det}</div>'
            f'  </div>'
            f'  {spk}'
            f'</div>'
        )

st.html("<div style='height:14px'></div>")

# ── If Search Active: Show Reset / Clear Button Banner ─────────────────────────
if is_filtered_search:
    ban_c1, ban_c2 = st.columns([4, 1.2])
    with ban_c1:
        if is_single_child:
            st.info(f"🔎 **Viewing Specific Child Record:** `{matched.iloc[0]['child_id']} · {matched.iloc[0]['full_name']}`. Showing **only this child's data**.")
        else:
            st.info(f"🔎 **Filtered Search Results:** Showing **{len(matched)}** children matching `{st.session_state['active_search_query']}`.")
    with ban_c2:
        st.button("✕ Reset & Show All Data", on_click=on_reset_click)

# ── Single-Child Dossier Card (Displayed only when specific child found) ────────
if is_single_child:
    c = matched.iloc[0]
    status_color = {
        "In HHS Care": "#38BDF8",
        "In CBP Custody": "#F97316",
        "Discharged to Sponsor": "#1ED760",
    }.get(c["current_status"], "#94A3B8")
    dossier_html = f"""<div class="dossier"><div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,.08);padding-bottom:12px;"><div><span class="dos-name">👤 {c['full_name']}</span>&nbsp;&nbsp;<span class="dos-id">{c['child_id']}</span></div><div style="font-size:.85rem;font-weight:700;color:{status_color}">● {c['current_status']}</div></div><div class="dos-grid"><div><div class="dos-lbl">Age &amp; Gender</div><div class="dos-val">{c['age']} yrs · {c['gender']}</div></div><div><div class="dos-lbl">Country of Origin</div><div class="dos-val">{c['country_of_origin']}</div></div><div><div class="dos-lbl">Shelter / Facility</div><div class="dos-val">{c['facility_name']}</div></div><div><div class="dos-lbl">Case Manager</div><div class="dos-val">{c['case_manager']}</div></div><div><div class="dos-lbl">Admission Date</div><div class="dos-val">{c['admission_date']} ({c['days_in_care']} days in care)</div></div><div><div class="dos-lbl">Discharge / Placement</div><div class="dos-val">{c['discharge_date']}</div></div><div><div class="dos-lbl">Medical Screening</div><div class="dos-val">{c['medical_status']}</div></div><div><div class="dos-lbl">Sponsor Vetting</div><div class="dos-val">{c['sponsor_relation']} · {c['sponsor_location']}<br><span style="font-size:.74rem;color:#A7A7A7">{c['sponsor_vetting_status']}</span></div></div></div></div>"""
    st.html(dossier_html)

# ── Row 2: Radial Utilization Arcs + Pipeline Flow Spline Chart ────────────────
col_arcs, col_flow = st.columns([1, 2])

with col_arcs:
    LICENSED = 10_000
    latest_r = df.iloc[-1]
    occ_val = min(100.0, float(latest_r["hhs_care"]) / LICENSED * 100)
    clear_val = min(100.0, period_dor * 100)
    cbp_c = float(latest_r["cbp_custody"])
    trs_c = float(latest_r["transfers_to_hhs"])
    transit_val = min(100.0, trs_c / max(1.0, cbp_c) * 100)

    def _arc(cx, cy, r, pct):
        p = max(0.02, min(0.98, pct / 100))
        a0 = -np.pi / 2
        a1 = a0 + 2 * np.pi * p
        x1, y1 = cx + r * np.cos(a0), cy + r * np.sin(a0)
        x2, y2 = cx + r * np.cos(a1), cy + r * np.sin(a1)
        lg = 1 if p > 0.5 else 0
        return f"M {x1:.2f} {y1:.2f} A {r} {r} 0 {lg} 1 {x2:.2f} {y2:.2f}"

    arc_svg = "".join([
        '<circle cx="95" cy="95" r="68" fill="none" stroke="#242424" stroke-width="11"/>',
        '<circle cx="95" cy="95" r="48" fill="none" stroke="#242424" stroke-width="11"/>',
        '<circle cx="95" cy="95" r="28" fill="none" stroke="#242424" stroke-width="11"/>',
        f'<path d="{_arc(95,95,68,occ_val)}" fill="none" stroke="#1ED760" stroke-width="11" stroke-linecap="round" style="filter:drop-shadow(0 0 6px rgba(30, 215, 96, 0.6))"/>',
        f'<path d="{_arc(95,95,48,clear_val)}" fill="none" stroke="#FBBF24" stroke-width="11" stroke-linecap="round" style="filter:drop-shadow(0 0 6px #FBBF24)"/>',
        f'<path d="{_arc(95,95,28,transit_val)}" fill="none" stroke="#00F2FE" stroke-width="11" stroke-linecap="round" style="filter:drop-shadow(0 0 6px #00F2FE)"/>',
    ])

    dot_row = lambda colour, label, pct: (
        f'<div style="display:flex;align-items:center;gap:10px">'
        f'<div style="width:12px;height:12px;border-radius:4px;background:{colour};box-shadow:0 0 8px {colour}"></div>'
        f'<div><div style="font-size:.73rem;color:#A7A7A7">{label}</div>'
        f'<div style="font-size:1.02rem;font-weight:700;color:#FFF">{pct:.1f}%</div></div>'
        f'</div>'
    )

    arcs_html = f"""<div class="glass" style="min-height:385px"><div class="g-title">Capacity &amp; Clearance Rates</div><div class="g-sub">Active Period Utilization Gauges</div><div style="display:flex;align-items:center;justify-content:space-around;padding-top:16px"><svg width="190" height="190" viewBox="0 0 190 190">{arc_svg}</svg><div style="display:flex;flex-direction:column;gap:14px">{dot_row("#1ED760", "HHS Bed Occupancy", occ_val)}{dot_row("#FBBF24", "Discharge Velocity", clear_val)}{dot_row("#00F2FE", "CBP Transit Turnover", transit_val)}</div></div><div style="margin-top:18px;padding:12px 14px;background:rgba(255,255,255,.03);border-radius:12px;border:1px solid rgba(255,255,255,.06);font-size:.77rem;color:#A7A7A7">💡 <b>Period Headroom:</b> {"Comfortable bed buffer." if occ_val < 75 else "⚠️ Elevated load – monitor staffing."}</div></div>"""
    st.html(arcs_html)

with col_flow:
    # Adapt chart data points based on chosen dimension
    if time_dimension == "📆 Month-Wise" and period_choice == "All Months (2023 – 2025 Aggregated)":
        df_plot = df.set_index("date").resample("ME").agg({
            "cbp_intake": "sum",
            "transfers_to_hhs": "sum",
            "discharges_from_hhs": "sum",
        }).reset_index()
        x_axis_pts = df_plot["date"]
        y_in = df_plot["cbp_intake"]
        y_tr = df_plot["transfers_to_hhs"]
        y_dis = df_plot["discharges_from_hhs"]
        chart_subtitle = "Monthly Aggregated Volumes (Border Inflow vs Transfers vs Discharges)"
    elif time_dimension == "📊 Week-Wise":
        df_plot = df.set_index("date").resample("W-SUN").agg({
            "cbp_intake": "sum",
            "transfers_to_hhs": "sum",
            "discharges_from_hhs": "sum",
        }).reset_index()
        x_axis_pts = df_plot["date"]
        y_in = df_plot["cbp_intake"]
        y_tr = df_plot["transfers_to_hhs"]
        y_dis = df_plot["discharges_from_hhs"]
        chart_subtitle = "Weekly Aggregated Volumes"
    else:
        x_axis_pts = df["date"]
        # Use 7-day smoothing if more than 30 points, else raw
        if len(df) > 30 and time_dimension != "⏱️ Day-Wise":
            y_in = df["cbp_intake"].rolling(7, min_periods=1).mean()
            y_tr = df["transfers_to_hhs"].rolling(7, min_periods=1).mean()
            y_dis = df["discharges_from_hhs"].rolling(7, min_periods=1).mean()
            chart_subtitle = "7-Day Smoothed Daily Trajectory"
        else:
            y_in = df["cbp_intake"]
            y_tr = df["transfers_to_hhs"]
            y_dis = df["discharges_from_hhs"]
            chart_subtitle = "Daily Operational Counts"

    fig_flow = go.Figure()
    fig_flow.add_trace(go.Scatter(
        x=x_axis_pts, y=y_in, mode="lines", name="CBP Intake (Inflow)",
        line=dict(color="#00F2FE", width=2.8, shape="spline")
    ))
    fig_flow.add_trace(go.Scatter(
        x=x_axis_pts, y=y_tr, mode="lines", name="HHS Transfers",
        line=dict(color="#A855F7", width=2.8, shape="spline")
    ))
    fig_flow.add_trace(go.Scatter(
        x=x_axis_pts, y=y_dis, mode="lines", name="Discharges (Outflow)",
        line=dict(color="#1ED760", width=3.0, shape="spline")
    ))
    fig_flow.update_layout(
        title=dict(
            text=f"<b>Pipeline Flow Dynamics</b> &nbsp;<span style='font-size:12px;color:#A7A7A7;font-weight:400'>{chart_subtitle}</span>",
            font=dict(color="#FFF", size=15)
        ),
        paper_bgcolor="#121212",
        plot_bgcolor="#121212",
        font=dict(color="#A7A7A7", size=11),
        margin=dict(l=30, r=20, t=55, b=25),
        height=385,
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="#E2E8F0", size=11), bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", zeroline=False, color="#71717A"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", zeroline=False, color="#71717A"),
    )
    st.plotly_chart(fig_flow, use_container_width=True, config={"displayModeBar": False})

# ── Row 3: Total System Care Load Area Chart + Day-of-Week Stacked Bars ────────
col_area, col_dow = st.columns([1.5, 1])

with col_area:
    if time_dimension == "📊 Week-Wise":
        df_area_plot = df.set_index("date").resample("W-SUN").agg({"total_system_load": "mean"}).reset_index()
        x_area = df_area_plot["date"]
        y_area = df_area_plot["total_system_load"]
        area_sub = "Weekly Average Load"
    elif time_dimension == "📆 Month-Wise" and period_choice == "All Months (2023 – 2025 Aggregated)":
        df_area_plot = df.set_index("date").resample("ME").agg({"total_system_load": "mean"}).reset_index()
        x_area = df_area_plot["date"]
        y_area = df_area_plot["total_system_load"]
        area_sub = "Monthly Average Load"
    else:
        x_area = df["date"]
        if len(df) > 30 and time_dimension != "⏱️ Day-Wise":
            y_area = df["total_system_load"].rolling(7, min_periods=1).mean()
            area_sub = "7-Day Smoothed"
        else:
            y_area = df["total_system_load"]
            area_sub = "Daily Actual"

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=x_area, y=y_area, mode="lines", name="Total System Load",
        line=dict(color="#1ED760", width=3.2, shape="spline"),
        fill="tozeroy", fillcolor="rgba(30, 215, 96, 0.18)",
    ))
    fig_area.add_hline(
        y=LICENSED, line_dash="dot", line_color="rgba(255,255,255,.3)",
        annotation_text=f"Licensed Capacity Limit ({LICENSED:,})",
        annotation_font_color="#A7A7A7", annotation_position="top right"
    )
    fig_area.update_layout(
        title=dict(
            text=f"<b>Total System Care Load – Census Trajectory</b> &nbsp;<span style='font-size:12px;color:#A7A7A7;font-weight:400'>{area_sub} ({time_dimension.split(' ')[1]})</span>",
            font=dict(color="#FFF", size=15)
        ),
        paper_bgcolor="#121212",
        plot_bgcolor="#121212",
        font=dict(color="#A7A7A7", size=11),
        margin=dict(l=30, r=20, t=55, b=25),
        height=360,
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", zeroline=False, color="#71717A"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", zeroline=False, color="#71717A"),
    )
    st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})

with col_dow:
    df_tmp = df.copy()
    df_tmp["day_name"] = df_tmp["date"].dt.day_name()
    ordered_days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    abbr_days = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
    dow_stat = df_tmp.groupby("day_name")[["transfers_to_hhs", "discharges_from_hhs"]].mean().reindex(ordered_days).fillna(0)

    fig_dow = go.Figure()
    fig_dow.add_trace(go.Bar(
        x=abbr_days, y=dow_stat["transfers_to_hhs"],
        name="Transfers to HHS",
        marker=dict(color="#8B5CF6", cornerradius=10)
    ))
    fig_dow.add_trace(go.Bar(
        x=abbr_days, y=dow_stat["discharges_from_hhs"],
        name="Discharges (Sponsors)",
        marker=dict(color="#1ED760", cornerradius=10)
    ))
    fig_dow.update_layout(
        title=dict(
            text="<b>Throughput / Week</b> &nbsp;<span style='font-size:12px;color:#A7A7A7;font-weight:400'>Daily Averages for Selected Period</span>",
            font=dict(color="#FFF", size=15)
        ),
        barmode="stack",
        paper_bgcolor="#121212",
        plot_bgcolor="#121212",
        bargap=0.36,
        font=dict(color="#A7A7A7", size=11),
        margin=dict(l=20, r=20, t=55, b=25),
        height=360,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="#E2E8F0", size=10), bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(showgrid=False, zeroline=False, color="#A7A7A7"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)", zeroline=False, color="#71717A"),
    )
    st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

# ── Row 4: Children Case Records Directory ─────────────────────────────────────
st.html("""<div class="glass"><div class="g-title">📋 Children Case Records &amp; Registry</div><div class="g-sub">Live Search Directory for Individual UAC Cases across CBP &amp; HHS Facilities</div></div>""")

# Case Directory Table
# USER REQUIREMENT:
# "in first picwhn we serch specific data then only show those data at that timr othrt time show requirad data all data"
if is_single_child:
    st.caption(f"Showing **only 1 matching child record** for `{matched.iloc[0]['child_id']} · {matched.iloc[0]['full_name']}`. All other records hidden.")
elif is_filtered_search:
    st.caption(f"Showing **{len(matched):,}** matching child record(s) · Filter active")
else:
    st.caption(f"Showing **all {len(matched):,}** registered children cases in system")

display_cols = {
    "child_id": "Child ID",
    "full_name": "Full Name",
    "age": "Age",
    "gender": "Gender",
    "country_of_origin": "Country",
    "current_status": "Status",
    "facility_name": "Shelter Facility",
    "admission_date": "Admitted",
    "days_in_care": "Days in Care",
    "sponsor_relation": "Sponsor Relation",
    "sponsor_location": "Placement City",
    "medical_status": "Medical Clearance",
}

# When specific search active: ONLY show matching rows (1 child if single search)
# Otherwise: show all children
st.dataframe(
    matched[list(display_cols)].rename(columns=display_cols),
    height=320 if not is_single_child else 120,
    use_container_width=True,
    hide_index=True,
)

# ── Row 5: Expandable Advanced Analytics & Tools ──────────────────────────────
with st.expander("🛠️ Advanced Analytics – Staffing, Surge Simulator & Data Audit", expanded=False):
    t_staff, t_sim, t_audit = st.tabs([
        "👥 Staffing Calculator",
        "🔮 Surge Simulator",
        "📋 Data Quality Audit",
    ])

    with t_staff:
        st.markdown("#### Federal ORR Child Welfare Staffing Requirements")
        active_now = int(df["hhs_care"].iloc[-1])
        st.caption(f"Based on current active HHS shelter census in selected period: **{active_now:,} children**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Direct Care Workers (1 : 8)", f"{int(np.ceil(active_now / 8)):,} FTEs")
        c2.metric("Bilingual Case Managers (1 : 10)", f"{int(np.ceil(active_now / 10)):,} FTEs")
        c3.metric("Mental Health Clinicians (1 : 25)", f"{int(np.ceil(active_now / 25)):,} FTEs")

    with t_sim:
        st.markdown("#### Influx Surge Scenario Stress-Test")
        s1, s2 = st.columns([1, 2])
        with s1:
            horizon = st.slider("Projection Horizon (days)", 14, 90, 30, step=7)
            shock_in = st.slider("Intake Shock (%)", -50, 100, 0, step=10)
            shock_out = st.slider("Discharge Delta (%)", -50, 50, 0, step=10)
        with s2:
            last_load = float(df["total_system_load"].iloc[-1])
            last14 = df.tail(min(len(df), 14))
            d_in = float(last14["transfers_to_hhs"].mean()) * (shock_in / 100)
            d_out = float(last14["discharges_from_hhs"].mean()) * (shock_out / 100)
            net = d_in - d_out
            proj_dates = [df["date"].iloc[-1] + timedelta(days=i) for i in range(1, horizon + 1)]
            proj_vals = [max(500.0, last_load + net * i) for i in range(1, horizon + 1)]

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(
                x=df["date"].tail(30), y=df["total_system_load"].tail(30),
                mode="lines", name="Recent Census", line=dict(color="#1ED760", width=2.5)))
            fig_sim.add_trace(go.Scatter(
                x=proj_dates, y=proj_vals, mode="lines", name="Simulated",
                line=dict(color="#EC4899", width=2.5, dash="dash")))
            fig_sim.add_hline(y=LICENSED, line_dash="dot", line_color="#EF4444",
                              annotation_text=f"Capacity Limit ({LICENSED:,})")
            fig_sim.update_layout(
                paper_bgcolor="#121212", plot_bgcolor="#121212",
                font=dict(color="#A7A7A7"), height=240,
                margin=dict(l=20, r=20, t=20, b=10))
            st.plotly_chart(fig_sim, use_container_width=True, config={"displayModeBar": False})

    with t_audit:
        st.markdown("#### Operational Reporting Integrity Audit")
        st.write(f"- **Selected Time Range:** {df['date'].min().strftime('%B %d, %Y')} "
                 f"→ {df['date'].max().strftime('%B %d, %Y')}  |  **{len(df):,}** operational records in view")
        st.write("- **Weekend gaps:** Friday/Saturday absences reflect the federal public-release "
                 "schedule (Sunday–Thursday). No internal data is lost.")
        st.write("- **Transfers > CBP custody (86 days):** Daily transfer counts represent "
                 "24-hour cumulative throughput; CBP custody is a point-in-time end-of-day snapshot.")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.html("""<div style="text-align:center;color:#71717A;font-size:.74rem;margin-top:2rem;padding-bottom:1rem">U.S. Department of Health and Human Services (HHS) &amp; Customs and Border Protection (CBP) &nbsp;|&nbsp; System Capacity &amp; Care Load Analytics &nbsp;|&nbsp; Spotify Dark Theme &nbsp;|&nbsp; Data: Jan 2023 – Dec 2025</div>""")
