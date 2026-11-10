"""
generate_children_registry.py
Generates realistic individual child case records aligned with HHS/CBP operational data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_children_registry(num_records=1200, seed=42):
    np.random.seed(seed)
    
    first_names_m = ["Mateo", "Santiago", "Carlos", "Diego", "Alejandro", "Luis", "Angel", "Jose", "Daniel", "Gabriel", "Samuel", "David", "Juan", "Lucas", "Miguel", "Sebastian"]
    first_names_f = ["Sofia", "Valentina", "Camila", "Isabella", "Maria", "Elena", "Lucia", "Mariana", "Gabriela", "Carmen", "Daniela", "Andrea", "Valeria", "Natalia", "Paula", "Ximena"]
    last_names = ["Hernandez", "Gonzalez", "Martinez", "Lopez", "Morales", "Rodriguez", "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez", "Diaz", "Cruz", "Reyes", "Morales", "Ortiz", "Gutierrez", "Chavez"]
    
    countries = ["Guatemala", "Honduras", "El Salvador", "Mexico", "Nicaragua", "Ecuador"]
    country_weights = [0.42, 0.28, 0.16, 0.08, 0.04, 0.02]
    
    hhs_facilities = [
        "Fort Bliss Influx Care Center (TX)",
        "Tornillo Emergency Care Facility (TX)",
        "San Antonio Children Center (TX)",
        "Harlingen Youth Residential (TX)",
        "Pecos Influx Shelter Center (TX)",
        "San Diego Youth Care Center (CA)",
        "Phoenix Transitional Shelter (AZ)",
        "Miami Family Reunification Center (FL)"
    ]
    
    cbp_facilities = [
        "Donna CBP Centralized Processing Facility (TX)",
        "El Paso Sector Central Processing Center (TX)",
        "Rio Grande Valley Border Patrol Station (TX)",
        "Tucson Sector Border Patrol Facility (AZ)",
        "Yuma Sector Holding Facility (AZ)"
    ]
    
    sponsor_relations = ["Mother", "Father", "Aunt / Uncle", "Grandmother", "Adult Sibling", "Vetted First Cousin"]
    sponsor_rel_weights = [0.38, 0.32, 0.16, 0.07, 0.05, 0.02]
    
    sponsor_cities = [
        "Houston, TX", "Los Angeles, CA", "Miami, FL", "Charlotte, NC",
        "Chicago, IL", "New York, NY", "Atlanta, GA", "Dallas, TX",
        "Phoenix, AZ", "Washington, DC", "Denver, CO", "Nashville, TN"
    ]
    
    case_managers = [
        "Dr. Elena Ramos, LCSW", "David Ortiz, MSW", "Sarah Jenkins, LCSW",
        "Carlos Mendez, Case Mgr", "Rachel Vance, MSW", "Dr. Marcus Thorne, MD",
        "Maria Solis, Lead Social Worker", "Ana Gutierrez, Bilingual Specialist"
    ]
    
    med_statuses = [
        "Cleared / Fully Vaccinated",
        "Medical Screening Complete",
        "Routine Dental/Vision Scheduled",
        "Standard Quarantine Window",
        "Pending Lab Results"
    ]
    med_weights = [0.65, 0.20, 0.08, 0.05, 0.02]
    
    # Statuses
    statuses = ["In HHS Care", "Discharged to Sponsor", "In CBP Custody"]
    status_weights = [0.45, 0.50, 0.05]
    
    records = []
    
    start_base = datetime(2023, 1, 15)
    end_base = datetime(2025, 12, 20)
    delta_days = (end_base - start_base).days
    
    for i in range(1, num_records + 1):
        # Child ID format: UAC-YYYY-XXXX
        year = np.random.choice([2023, 2024, 2025], p=[0.30, 0.45, 0.25])
        child_id = f"UAC-{year}-{i:04d}"
        
        gender = np.random.choice(["Male", "Female"], p=[0.58, 0.42])
        first_name = np.random.choice(first_names_m) if gender == "Male" else np.random.choice(first_names_f)
        last_name = np.random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        age = int(np.random.choice(range(4, 18), p=[0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.11, 0.13, 0.14, 0.11, 0.05, 0.02]))
        country = np.random.choice(countries, p=country_weights)
        
        status = np.random.choice(statuses, p=status_weights)
        
        # Admission date
        rand_day = np.random.randint(0, delta_days)
        admission_dt = start_base + timedelta(days=rand_day)
        if year == 2025:
            admission_dt = datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 350))
        elif year == 2024:
            admission_dt = datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 360))
        elif year == 2023:
            admission_dt = datetime(2023, 1, 15) + timedelta(days=np.random.randint(0, 345))
            
        if status == "In CBP Custody":
            facility = np.random.choice(cbp_facilities)
            days_in_care = np.random.randint(1, 4) # 72h rule
            discharge_dt = None
            sponsor_status = "Triage / Preparing HHS Transfer"
            sponsor_rel = "Pending Verification"
            sponsor_loc = "Pending Intake"
        elif status == "In HHS Care":
            facility = np.random.choice(hhs_facilities)
            days_in_care = np.random.randint(5, 45)
            discharge_dt = None
            sponsor_rel = np.random.choice(sponsor_relations, p=sponsor_rel_weights)
            sponsor_loc = np.random.choice(sponsor_cities)
            sponsor_status = np.random.choice(["Background Check in Progress", "Home Study Underway", "Fingerprint Cleared", "Final Sponsor Vetting"])
        else: # Discharged
            facility = np.random.choice(hhs_facilities)
            days_in_care = np.random.randint(12, 38)
            discharge_dt = admission_dt + timedelta(days=days_in_care)
            sponsor_rel = np.random.choice(sponsor_relations, p=sponsor_rel_weights)
            sponsor_loc = np.random.choice(sponsor_cities)
            sponsor_status = "Reunified with Sponsor (Completed)"
            
        med_status = np.random.choice(med_statuses, p=med_weights)
        case_mgr = np.random.choice(case_managers)
        
        records.append({
            'child_id': child_id,
            'full_name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'gender': gender,
            'country_of_origin': country,
            'current_status': status,
            'facility_name': facility,
            'admission_date': admission_dt.strftime('%Y-%m-%d'),
            'discharge_date': discharge_dt.strftime('%Y-%m-%d') if discharge_dt else "N/A",
            'days_in_care': days_in_care,
            'sponsor_relation': sponsor_rel,
            'sponsor_location': sponsor_loc,
            'sponsor_vetting_status': sponsor_status,
            'medical_status': med_status,
            'case_manager': case_mgr
        })
        
    df_reg = pd.DataFrame(records)
    df_reg.to_csv('uac_children_registry.csv', index=False)
    print(f"Generated {len(df_reg)} child records successfully.")
    print(df_reg.head(3))

if __name__ == '__main__':
    create_children_registry()
