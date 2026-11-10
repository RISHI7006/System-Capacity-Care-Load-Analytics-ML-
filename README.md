# System Capacity & Care Load Analytics for Unaccompanied Children (UAC)

This repository contains the complete analytical framework, research paper, executive summary, and interactive Streamlit web dashboard for monitoring the U.S. Unaccompanied Alien Children (UAC) care pipeline across **U.S. Customs and Border Protection (CBP)** and the **Department of Health and Human Services (HHS / ORR)**.

---

## 📁 Repository Structure & Deliverables

| File | Description |
| :--- | :--- |
| **`app.py`** | **Interactive Streamlit Web Dashboard** featuring 5 core panes: System Load Overview, CBP vs HHS Comparison, Inflow/Outflow/Backlog Trends, Predictive Capacity Simulator, and Data Quality & Policy Guide. |
| **`data_loader.py`** | Modular data processing pipeline that cleans data, handles missing dates, validates logical constraints, and engineers derived healthcare capacity metrics. |
| **`RESEARCH_PAPER_SYSTEM_CAPACITY_UAC.md`** | **Comprehensive Technical Research Paper** detailing the healthcare systems engineering perspective, mathematical formulations, exploratory findings, strain window diagnoses, and policy recommendations. |
| **`EXECUTIVE_SUMMARY_UAC_STAKEHOLDERS.md`** | **High-Level Executive Briefing Document** tailored for HHS/ORR, CBP, OMB, and federal policymakers, featuring KPI scorecards, risk matrices, and SOP recommendations. |
| **`HHS_Unaccompanied_Alien_Children_Program (1).csv`** | Official daily operational dataset spanning January 2023 through December 2025 (720 reporting records). |
| **`analysis_pipeline.py` / `explore_uac.py`** | Analytical and diagnostic scripts used to audit data quality and compute multi-year regime statistics. |

---

## 🚀 How to Run the Streamlit Dashboard

To launch the interactive dashboard on your local machine:

```powershell
streamlit run app.py
```

Or run via python module:
```powershell
python -m streamlit run app.py
```

Once launched, open your web browser to `http://localhost:8501`.

---

## 🎯 Key Dashboard Capabilities

1. **System Load Overview Pane:**
   - Stacked area and multi-line visual of total children under federal care (CBP holding custody + HHS care facilities).
   - Dynamic 85% pre-surge warning and 100% capacity threshold lines.
2. **CBP vs HHS Load Dynamics:**
   - Dual-axis time-series tracing the interaction between CBP holding headcounts and HHS residential census.
   - CBP 24-hour turnover efficiency index and three-stage pipeline flow tracking.
3. **Net Intake & Backlog Trajectory:**
   - Daily net intake pressure bars (red for accumulation strain, green for system relief) with 7-day rolling smoothing.
   - Cumulative care backlog accumulation curve and Discharge Offset Ratio (DOR) monitoring.
4. **Predictive Capacity Modeling & Influx Stress Simulator:**
   - Adjustable forecast horizon (14 to 90 days) with confidence interval bands (90%, 95%, 99%).
   - Interactive shock simulation sliders for intake surges (-50% to +100%) and discharge velocity shifts (-50% to +50%).
   - Automated early warning risk status alerts.
5. **Data Quality & Healthcare Staffing Calculator:**
   - Audit report explaining reporting cadence (Friday/Saturday release schedules) and continuous throughput vs snapshot headcounts.
   - Live ORR-mandated staffing calculator (Direct Care Workers 1:8, Case Managers 1:10, Mental Health Clinicians 1:25).
   - Filtered dataset export to CSV.
