import pandas as pd
import numpy as np

df = pd.read_csv('HHS_Unaccompanied_Alien_Children_Program (1).csv').dropna(how='all')
df['date'] = pd.to_datetime(df['Date'])
cols = {
    'Children apprehended and placed in CBP custody*': 'cbp_intake',
    'Children in CBP custody': 'cbp_custody',
    'Children transferred out of CBP custody': 'transfers_to_hhs',
    'Children in HHS Care': 'hhs_care',
    'Children discharged from HHS Care': 'discharges_from_hhs'
}
for old, new in cols.items():
    df[new] = pd.to_numeric(df[old].astype(str).str.replace(',', '').str.strip(), errors='coerce')

df = df.sort_values('date').reset_index(drop=True)
df['total_system_load'] = df['cbp_custody'] + df['hhs_care']
df['net_hhs_intake'] = df['transfers_to_hhs'] - df['discharges_from_hhs']
df['net_pipeline_flow'] = df['cbp_intake'] - df['discharges_from_hhs']
df['discharge_offset_ratio'] = np.where(df['transfers_to_hhs'] > 0, df['discharges_from_hhs'] / df['transfers_to_hhs'], np.nan)
df['year'] = df['date'].dt.year

print("--- Yearly Statistics ---")
for y, group in df.groupby('year'):
    print(f"Year {y} (N={len(group)} reports):")
    print(f"  CBP Intake: Mean={group['cbp_intake'].mean():.1f}, Median={group['cbp_intake'].median():.1f}, Max={group['cbp_intake'].max():.0f}, Total={group['cbp_intake'].sum():.0f}")
    print(f"  CBP Custody: Mean={group['cbp_custody'].mean():.1f}, Median={group['cbp_custody'].median():.1f}, Max={group['cbp_custody'].max():.0f}")
    print(f"  Transfers to HHS: Mean={group['transfers_to_hhs'].mean():.1f}, Total={group['transfers_to_hhs'].sum():.0f}")
    print(f"  HHS Care: Mean={group['hhs_care'].mean():.1f}, Median={group['hhs_care'].median():.1f}, Min={group['hhs_care'].min():.0f}, Max={group['hhs_care'].max():.0f}")
    print(f"  Discharges: Mean={group['discharges_from_hhs'].mean():.1f}, Total={group['discharges_from_hhs'].sum():.0f}")
    print(f"  Total System Load: Mean={group['total_system_load'].mean():.1f}, Min={group['total_system_load'].min():.0f}, Max={group['total_system_load'].max():.0f}")
    print(f"  Net HHS Intake: Mean={group['net_hhs_intake'].mean():.1f}, Cumulative={group['net_hhs_intake'].sum():.0f}")
    print(f"  Discharge Offset Ratio: Mean={group['discharge_offset_ratio'].mean():.2f}, Median={group['discharge_offset_ratio'].median():.2f}")
    print()

print("--- Peak Stress Periods (Top 10 Total System Load) ---")
print(df.sort_values('total_system_load', ascending=False)[['date', 'total_system_load', 'cbp_custody', 'hhs_care', 'cbp_intake', 'transfers_to_hhs', 'discharges_from_hhs']].head(10).to_string())

print("\n--- Minimum Load Periods (Bottom 10 Total System Load) ---")
print(df.sort_values('total_system_load', ascending=True)[['date', 'total_system_load', 'cbp_custody', 'hhs_care', 'cbp_intake', 'transfers_to_hhs', 'discharges_from_hhs']].head(10).to_string())

print("\n--- Major Inflow Surges (Top 10 Net HHS Intake) ---")
print(df.sort_values('net_hhs_intake', ascending=False)[['date', 'net_hhs_intake', 'transfers_to_hhs', 'discharges_from_hhs', 'total_system_load']].head(10).to_string())

print("\n--- Major Relief Days (Top 10 Net Outflow / Negative Net Intake) ---")
print(df.sort_values('net_hhs_intake', ascending=True)[['date', 'net_hhs_intake', 'transfers_to_hhs', 'discharges_from_hhs', 'total_system_load']].head(10).to_string())
