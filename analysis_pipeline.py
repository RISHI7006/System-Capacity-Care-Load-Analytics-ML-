import pandas as pd
import numpy as np

def run_analysis():
    # Load dataset
    df = pd.read_csv('HHS_Unaccompanied_Alien_Children_Program (1).csv')
    df = df.dropna(how='all').copy()
    
    # Rename columns for ease of manipulation
    col_mapping = {
        'Date': 'date',
        'Children apprehended and placed in CBP custody*': 'cbp_intake',
        'Children in CBP custody': 'cbp_custody',
        'Children transferred out of CBP custody': 'transfers_to_hhs',
        'Children in HHS Care': 'hhs_care',
        'Children discharged from HHS Care': 'discharges_from_hhs'
    }
    df = df.rename(columns=col_mapping)
    
    # Clean numeric columns (remove commas, cast to float/int)
    numeric_cols = ['cbp_intake', 'cbp_custody', 'transfers_to_hhs', 'hhs_care', 'discharges_from_hhs']
    for col in numeric_cols:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print("=== DATASET OVERVIEW ===")
    print(f"Total non-empty records: {len(df)}")
    print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"Total calendar days span: {(df['date'].max() - df['date'].min()).days + 1}")
    
    # Check duplicate dates
    dup_dates = df[df.duplicated(subset=['date'], keep=False)]
    print(f"Duplicate dates count: {len(dup_dates)}")
    
    # Check missing dates in the sequence
    full_date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
    missing_dates = full_date_range.difference(df['date'])
    print(f"Missing calendar dates count: {len(missing_dates)}")
    print(f"Missing dates sample (first 10): {[d.strftime('%Y-%m-%d') for d in missing_dates[:10]]}")
    
    # Logical constraints validation:
    # 1. Transfers <= CBP custody ? Note: Transfers out of CBP custody on a day vs snapshot of CBP custody or inflow
    # In some datasets, transfers might exceed end-of-day custody if custody is an end-of-day count after transfers.
    # Let's inspect transfers vs cbp_custody
    transfers_gt_custody = df[df['transfers_to_hhs'] > df['cbp_custody']]
    print(f"\nInstances where transfers_to_hhs > cbp_custody: {len(transfers_gt_custody)}")
    if len(transfers_gt_custody) > 0:
        print(transfers_gt_custody[['date', 'cbp_intake', 'cbp_custody', 'transfers_to_hhs']].head())
        
    discharges_gt_care = df[df['discharges_from_hhs'] > df['hhs_care']]
    print(f"Instances where discharges_from_hhs > hhs_care: {len(discharges_gt_care)}")
    
    # Derived Healthcare Capacity Metrics
    df['total_system_load'] = df['cbp_custody'] + df['hhs_care']
    df['net_daily_intake'] = df['transfers_to_hhs'] - df['discharges_from_hhs'] # HHS net intake
    df['total_net_system_flow'] = df['cbp_intake'] - df['discharges_from_hhs'] # Entire pipeline inflow vs outflow
    df['care_load_growth_rate'] = df['total_system_load'].pct_change() * 100
    df['discharge_offset_ratio'] = np.where(df['transfers_to_hhs'] > 0, df['discharges_from_hhs'] / df['transfers_to_hhs'], np.nan)
    df['cbp_turnover_rate'] = np.where(df['cbp_custody'] > 0, df['transfers_to_hhs'] / df['cbp_custody'], np.nan)
    
    # Rolling averages
    df['total_load_7d_avg'] = df['total_system_load'].rolling(7, min_periods=1).mean()
    df['total_load_14d_avg'] = df['total_system_load'].rolling(14, min_periods=1).mean()
    df['net_intake_7d_avg'] = df['net_daily_intake'].rolling(7, min_periods=1).mean()
    
    # Cumulative backlog accumulation
    df['cumulative_backlog'] = df['net_daily_intake'].cumsum()
    
    # Summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(df[['cbp_intake', 'cbp_custody', 'transfers_to_hhs', 'hhs_care', 'discharges_from_hhs', 'total_system_load', 'net_daily_intake', 'discharge_offset_ratio']].describe().T[['mean', 'std', 'min', '50%', 'max']])
    
    # Yearly breakdown
    df['year'] = df['date'].dt.year
    print("\n=== YEARLY BREAKDOWN ===")
    yearly = df.groupby('year').agg({
        'cbp_intake': ['mean', 'max'],
        'cbp_custody': ['mean', 'max'],
        'transfers_to_hhs': ['mean', 'sum'],
        'hhs_care': ['mean', 'min', 'max'],
        'discharges_from_hhs': ['mean', 'sum'],
        'total_system_load': ['mean', 'max'],
        'net_daily_intake': ['mean', 'sum']
    })
    print(yearly)
    
    # Save cleaned daily and resampled daily datasets
    df.to_csv('cleaned_uac_data.py_output.csv', index=False)
    
    # Also create interpolated complete daily dataset
    df_indexed = df.set_index('date').sort_index()
    df_daily = df_indexed.reindex(full_date_range)
    df_daily.index.name = 'date'
    # Interpolate for continuous time series
    df_daily_interpolated = df_daily.interpolate(method='time')
    df_daily_interpolated.to_csv('interpolated_daily_uac.csv')
    print("\nSaved cleaned and interpolated datasets.")

if __name__ == '__main__':
    run_analysis()
