from datetime import timedelta
import pandas as pd 

source_path = '/Users/beatricianagit/process_mining_project/data/raw/source_data.csv'

rename_map = {
    # Case & demographics
    "ID": "case_id",
    "PS": "emergency_room",                
    "Scheda_PS": "file_id",
    "Sesso": "sex",
    "Data_Nascita": "birthday",
    "Comune_Res": "residence_city",
    "Regione_Res": "residence_region",
    "Mod_Arrivo": "arrival_method",
    "Reparto": "department",
    "eta_paziente": "age",
    "etapaziente_ric": "age_group",
    "Triage_Ingr": "TRIAGE_ENTRY_SEVERITY", # this is for TRIAGE_ENTRY.severity
    "Triage_OUT": "TRIAGE_OUT_SEVERITY", # this is for TRIAGE_OUT.severity


    # Core timestamps 
    # ts - timestamp
    "data_arrivo_tot": "ARRIVAL_ts",
    "Presa_In_Carico": "ACCEPTANCY_ts",
    "data_dimissione_tot": "DISCHARGE_ts",

    # Outcome -> becomes OUTCOME_* activity later
    "Esito": "OUTCOME_raw", # will be changed to OUTCOME_Ricovero, OUTCOME_Dimissione_a_domicilio later

    # DISCHARGE attributes
    "Medico_Dimissione": "DISCHARGE_doctor",
    "Diag_TXT": "DISCHARGE_diagnosis_description",
    "Diagnosi_Classe": "DISCHARGE_diagnosis_class",
    "Diagnosi_Codice": "DISCHARGE_diagnosis_code",

    # VISIT and tests
    "CODICE_RICHIESTA": "visit_code",
    "DESCR_PRESTAZIONE": "visit_description",
    "DESCR_EROGATORE": "test_department",  
    "DATA_PREVISTA_EROGAZIONE": "test_planned_ts"
}

timestamp_columns = [
    "ARRIVAL_ts", 
    "ACCEPTANCY_ts", 
    "DISCHARGE_ts", 
    "test_planned_ts"
]

def run_full_clean(source_path, rename_map, timestamp_columns, preview_path="clean_db_preview.csv", n_preview=10):
    df_sample = pd.read_csv(source_path, low_memory=False)

    # Working only with patient data from PS Generale
    df_sample = df_sample[df_sample["PS"] == 'PS GENERALE'].copy()
    
    # Renaming columns
    df_sample = df_sample.rename(columns=rename_map)
    
    # Keep only needed columns
    columns_to_keep = list(rename_map.values())
    clean_db = df_sample[[c for c in columns_to_keep if c in df_sample.columns]].copy()

    # converting timestamps to datetime
    # 2023-01-01 21:19:00 -> real datetime object
    for col in timestamp_columns:
        if col in clean_db.columns:
            clean_db[col] = pd.to_datetime(clean_db[col], errors="coerce")
    
    # creating synthetic timestamps for TRIAGE_ENTRY and TRIAGE_OUT
    if "ARRIVAL_ts" in clean_db.columns:
        clean_db["TRIAGE_ENTRY_ts"] = clean_db["ARRIVAL_ts"] + timedelta(seconds=1)
    if "ACCEPTANCY_ts" in clean_db.columns:
        clean_db["TRIAGE_OUT_ts"] = clean_db["ACCEPTANCY_ts"] + timedelta(seconds=1)

    # Save a small preview for wide tables
    clean_db.head(n_preview).to_csv(preview_path, index=False)

    return clean_db

clean_db = run_full_clean(source_path, rename_map, timestamp_columns)