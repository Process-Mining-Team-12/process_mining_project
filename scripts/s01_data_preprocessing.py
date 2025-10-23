from datetime import timedelta
import pandas as pd 

INPUT_CSV = 'data/raw/source_data.csv'
OUTPUT_CSV = 'data/raw/filtered_data.csv'

COLUMN = "DESCR_EROGATORE"
REMOVE_VALUES = [
	"PS Gen AO CASERTA",
    "IMMUNOEMATOLOGIA E CENTRO TRASFUSIONALE - AMBULATORIO (PER ESTERNI)",
    "TERAPIA DEL DOLORE - AMBULATORIO",
    "REPARTO AMBULATORIALE CHIRURGIA D'URGENZA",
    "GERIATRIA - AMBULATORIO",
    "STROKE UNIT - AMBULATORIO",
    "CARDIOCHIRURGIA - AMBULATORIO",
    "PEDIATRIA - AMBULATORIO",
    "OSTETRICIA E GINECOLOGIA A DIREZIONE UNIVERSITARIA - AMBULATORIO",
]

RENAME_MAP = {
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
    "Triage_Ingr": "triage_entry_severity", # this is for TRIAGE_ENTRY.severity
    "Triage_OUT": "triage_exit_severity", # this is for TRIAGE_EXIT.severity

    # Core timestamps 
    # ts - timestamp
    "data_arrivo_tot": "arrival_ts",
    "Presa_In_Carico": "acceptancy_ts",
    "data_dimissione_tot": "outcome_ts",

    # Outcome -> becomes OUTCOME_* activity later
    "Esito": "outcome_raw", # will be changed to OUTCOME_Ricovero, OUTCOME_Dimissione_a_domicilio later

    # DISCHARGE attributes
    "Medico_Dimissione": "discharge_doctor",
    "Diag_TXT": "discharge_diagnosis_description",
    "Diagnosi_Classe": "discharge_diagnosis_class",
    "Diagnosi_Codice": "discharge_diagnosis_code",

    # VISIT and tests
    "CODICE_RICHIESTA": "visit_code",
    "DESCR_PRESTAZIONE": "visit_description",
    "DESCR_EROGATORE": "test_department",  
    "DATA_PREVISTA_EROGAZIONE": "test_planned_ts"
}

TIMESTAMP_COLUMNS = [
    "arrival_ts", 
    "acceptancy_ts", 
    "outcome_ts", 
    "test_planned_ts"
]

OUTCOME_MAP = {
    "Rifiuta ricovero": "Refused admission",
    "Dimissione a strutture ambulatoriali": "Outpatient discharge",
    "Ricovero": "Admitted",
    "Dimissione a domicilio": "Home discharge",
    "Abbandona prima della chiusura della cartella": "Left early",
    "Trasferito ad altro Ospedale": "Hospital transfer",
    "Deceduto in PS": "Died in ER",
    "Trasferito in struttura territoriale": "Local transfer",
    "Giunto cadavere": "Arrived dead"
}

def filter_data():
    df = pd.read_csv(INPUT_CSV, low_memory=False)

    # Strip spaces from all string columns
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # Working only with patient data from PS Generale
    df = df[df["PS"] == "PS GENERALE"]

    # Find IDs that have at least one row with a value to remove in the target column
    ids_to_remove = df.loc[df[COLUMN].isin(REMOVE_VALUES), "ID"].dropna().unique()

    # Drop all rows whose ID is in that set
    df = df[~df["ID"].isin(ids_to_remove)]
    
    # Renaming columns
    df = df.rename(columns=RENAME_MAP)

    # Map outcome_raw column to short english names
    df["outcome_raw"] = df["outcome_raw"].map(OUTCOME_MAP)
    
    # Keep only needed columns
    columns_to_keep = list(RENAME_MAP.values())
    df_filtered = df[[c for c in columns_to_keep if c in df.columns]].copy()

    # converting timestamps to datetime
    # 2023-01-01 21:19:00 -> real datetime object
    for col in TIMESTAMP_COLUMNS:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_datetime(df_filtered[col], errors="coerce")
    
    # creating synthetic timestamps for TRIAGE_ENTRY and TRIAGE_EXIT
    if "arrival_ts" in df_filtered.columns:
        df_filtered["triage_entry_ts"] = df_filtered["arrival_ts"] + timedelta(milliseconds=1)
    if "outcome_ts" in df_filtered.columns:
        df_filtered["triage_exit_ts"] = df_filtered["outcome_ts"] + timedelta(milliseconds=1)
        df_filtered["discharge_ts"] = df_filtered["outcome_ts"] + timedelta(milliseconds=2)

    return df_filtered

def save_data(df):
    df.to_csv(OUTPUT_CSV, index=False)

if __name__ == "__main__":
    df_filtered = filter_data()
    save_data(df_filtered)
