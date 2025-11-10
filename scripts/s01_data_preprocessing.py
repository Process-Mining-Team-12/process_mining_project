"""Data Preprocessing Script"""
from datetime import timedelta
from pathlib import Path
import pandas as pd

INPUT_CSV = Path("data/raw/source_data.csv")
OUTPUT_CSV = Path("data/raw/filtered_data.csv")

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
    "Triage_Ingr": "triage_entry_severity",
    "Triage_OUT": "triage_exit_severity",

    # Core timestamps
    "data_arrivo_tot": "arrival_ts",
    "Presa_In_Carico": "acceptancy_ts",
    "data_dimissione_tot": "outcome_ts",

    # Outcome
    "Esito": "outcome_raw",

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

TEST_DEPARTMENT_RENAMING_MAPPING = {
    'LAB. ANALISI': 'TEST',
    'RADIOLOGIA': 'RADIOLOGY_DEPT',
    'U.O.S.D. NEURORADIOLOGIA': 'NEURORADIOLOGY',
    'GASTROENTEROLOGIA - AMBULATORIO': 'GASTROENTEROLOGY',
    'NEFROLOGIA - AMBULATORIO': 'NEPHROLOGY',
    'DERMATOLOGIA E MALATTIE VENEREE - AMBULATORIO': 'DERMATOLOGY',
    'MEDICINA INTERNA - AMBULATORIO': 'INTERNAL_MEDICINE',
    'NEUROLOGIA - AMBULATORIO': 'NEUROLOGY',
    'PNEUMOLOGIA FISIOPATOLOGIA RESPIRATORIA - AMBULATORIO': 'PULMONOLOGY',
    'REPARTO AMBULATORIALE ALLERGOLOGIA': 'ALLERGOLOGY_AMB',
    "CARDIOLOGIA D'EMERGENZA CON UTIC - AMBULATORIO": 'EMERGENCY_CARDIOLOGY_UTIC',
    'MALATTIE  INFETTIVE E TROPICALI A DIREZIONE UNIVERSITARIA - AMBULATORIO - EROGAZIONE FARMACI PER ESTERNI': 'INFECTIOUS_DISEASES_PHARMACY',
    'Eliot': 'ELIOT_TRANSFUSION',
    'NEUROCHIRURGIA - AMBULATORIO': 'NEUROSURGERY',
    'ORTOPEDIA E TRAUMATOLOGIA - AMBULATORIO': 'ORTHOPEDICS_TRAUMA',
    'OTORINOLARINGOIATRIA - AMBULATORIO': 'ENT_OTOLARYNGOLOGY',
    'UROLOGIA - AMBULATORIO': 'UROLOGY',
    'REPARTO AMBULATORIALE CHIRURGIA VASCOLARE': 'VASCULAR_SURGERY_AMB',
    'REPARTO AMBULATORIALE CH.MAX.ODONTOST.': 'MAXILLOFACIAL_SURGERY_AMB',
    'REPARTO AMBULATORIALE ANESTESIA E RIANIMAZIONE': 'ANESTHESIA_RESUSCITATION_AMB',
    'REPARTO AMBULATORIALE ONCOLOGIA': 'ONCOLOGY_GENERAL',
    'CHIRURGIA GENERALE ED ONCOLOGICA - AMBULATORIO': 'ONCOLOGY_SURGERY',
    'EMATOLOGIA AD INDIRIZZO ONCOLOGICO - AMBULATORIO': 'ONCOLOGY_HEMATOLOGY',
    'FOLLOW UP DEL PAZIENTE POST ACUTO - AMBULATORIO': 'POST_ACUTE_FOLLOW_UP'
}

TEST_DEPARTMENT_GROUPING = {
    "TESTS": ["TEST"],
    "RADIOLOGY": [
        "RADIOLOGY_DEPT",
        "NEURORADIOLOGY"],
    "MEDICAL": [
        "GASTROENTEROLOGY",
        "NEPHROLOGY",
        "DERMATOLOGY",
        "INTERNAL_MEDICINE",
        "NEUROLOGY",
        "PULMONOLOGY",
        "ALLERGOLOGY_AMB",
        "EMERGENCY_CARDIOLOGY_UTIC",
        "INFECTIOUS_DISEASES_PHARMACY",
        "ELIOT_TRANSFUSION"],
    "SURGERY": [
        "NEUROSURGERY",
        "ORTHOPEDICS_TRAUMA",
        "ENT_OTOLARYNGOLOGY",
        "UROLOGY",
        "VASCULAR_SURGERY_AMB",
        "MAXILLOFACIAL_SURGERY_AMB"],
    "INTENSIVE": ["ANESTHESIA_RESUSCITATION_AMB"],
    "ONCOLOGY": [
        "ONCOLOGY_GENERAL",
        "ONCOLOGY_SURGERY",
        "ONCOLOGY_HEMATOLOGY"],
    "FOLLOW_UP": ["POST_ACUTE_FOLLOW_UP"],
}

TIMESTAMP_COLUMNS = [
    "arrival_ts",
    "acceptancy_ts",
    "outcome_ts",
    "test_planned_ts",
]

OUTCOME_MAP = {
    "Rifiuta ricovero": "REFUSED_ADMISSION",
    "Dimissione a strutture ambulatoriali": "OUTPATIENT_DISCHARGE",
    "Ricovero": "ADMITTED",
    "Dimissione a domicilio": "HOME_DISCHARGE",
    "Abbandona prima della chiusura della cartella": "LEFT_EARLY",
    "Trasferito ad altro Ospedale": "HOSPITAL_TRANSFER",
    "Deceduto in PS": "DIED_ER",
    "Trasferito in struttura territoriale": "LOCAL_TRANSFER",
    "Giunto cadavere": "ARRIVED_DEAD",
}

SEVERITY_MAP = {
    "Arancione": "ORANGE",
    "Azzurro": "BLUE",
    "Bianco": "WHITE",
    "Nero": "BLACK",
    "Rosso": "RED",
    "Verde": "GREEN",
}


def load_data(filepath: Path) -> pd.DataFrame:
    """Load CSV data from the given path."""
    return pd.read_csv(filepath, low_memory=False)


def update_outcome_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Fix the time zone adding one hour to outcome timestamp"""
    date_hour_string = df["Data_Dimissione"] + ' ' + df["Ora_Dimissione"]
    df["data_dimissione_tot"] = pd.to_datetime(date_hour_string)
    return df


def update_arrival_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Fix the time zone adding one hour to arrival timestamp"""
    date_hour_string = df["Data_Arrivo"] + ' ' + df["Ora_Arrivo"]
    df["data_arrivo_tot"] = pd.to_datetime(date_hour_string)
    return df


def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip spaces from all string columns."""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()
    return df


def filter_emergency_room(df: pd.DataFrame, er_name: str = "PS GENERALE") -> pd.DataFrame:
    """Keep only rows where PS equals the specified emergency room name."""
    return df[df["emergency_room"] == er_name]


def drop_invalid_exams(df: pd.DataFrame, to_remove: list[str]) -> pd.DataFrame:
    """Remove all patients whose ID appears with a given column value in `values_to_remove`."""
    ids_to_remove = df.loc[
        df["test_department"].isin(to_remove),
        "case_id"
    ].dropna().unique()
    return df[~df["case_id"].isin(ids_to_remove)]


def rename_columns(df: pd.DataFrame, rename_map: dict[str, str]) -> pd.DataFrame:
    """Rename DataFrame columns according to the given mapping."""
    return df.rename(columns=rename_map)


def translate_test_department(df: pd.DataFrame, translation_map: dict[str, str]) -> pd.DataFrame:
    """Translate department names to english accorging to the given mapping. """
    return df.replace(translation_map)


def create_test_department_group(df: pd.DataFrame, group_map: dict[str, str]) -> pd.DataFrame:
    """Create test department groups based on the given group map. """
    # invert the mapping so each value maps to its group
    value_to_group = {
        value: group
        for group, values in group_map.items()
        for value in values
    }
    df["test_department_group"] = df["test_department"].map(value_to_group)
    return df


def map_outcome_values(df: pd.DataFrame) -> pd.DataFrame:
    """Map Italian outcome descriptions to English ones."""
    df["outcome_raw"] = df["outcome_raw"].map(OUTCOME_MAP)
    return df


def map_triage_severity_values(df: pd.DataFrame):
    """Map Italian triage severity descriptions to English ones."""
    df["triage_entry_severity"] = df["triage_entry_severity"].map(SEVERITY_MAP)
    df["triage_exit_severity"] = df["triage_exit_severity"].map(SEVERITY_MAP)
    return df


def filter_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Keep only specified columns that exist in the DataFrame."""
    existing = [c for c in columns if c in df.columns]
    return df[existing].copy()


def convert_timestamps(df: pd.DataFrame, timestamp_cols: list[str]) -> pd.DataFrame:
    """Convert timestamp columns to datetime, coercing errors."""
    for col in timestamp_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], errors="coerce").dt.tz_localize("Etc/GMT-1")
    return df


def add_synthetic_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Add synthetic timestamps for triage and discharge events."""
    if "arrival_ts" in df.columns:
        df["triage_entry_ts"] = df["arrival_ts"] + timedelta(seconds=1)
    if "outcome_ts" in df.columns:
        df["triage_exit_ts"] = df["outcome_ts"] + timedelta(seconds=1)
        df["discharge_ts"] = df["outcome_ts"] + timedelta(seconds=2)
    return df


def dropna_by_column(df: pd.DataFrame, column: str):
    """Remove all patients who have a NaN value in the specified column."""
    ids_to_remove = df.loc[df[column].isna(), "case_id"].dropna().unique()
    return df[~df["case_id"].isin(ids_to_remove)]


def drop_invalid_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Remove all patients with invalid timestamps."""
    ids_to_remove = df.loc[
        (df["acceptancy_ts"] >= df["triage_exit_ts"])
        | (df["acceptancy_ts"] <= df["arrival_ts"]),
        "case_id"
    ].dropna().unique()
    return df[~df["case_id"].isin(ids_to_remove)]


def drop_2024_records(df: pd.DataFrame, timestamp_cols: list[str]) -> pd.DataFrame:
    """Remove all recordds with the discharge timestamp in 2024."""
    ids_to_remove = []
    for col in timestamp_cols:
        ids_to_remove.extend(
            df.loc[df[col].dt.year >= 2024, "case_id"].dropna().unique()
        )
    return df[~df["case_id"].isin(ids_to_remove)]


def save_data(df: pd.DataFrame, filepath: Path) -> None:
    """Save DataFrame to CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)


def process_data(input_path: Path, output_path: Path) -> None:
    """Execute the full filtering and cleaning pipeline."""
    df = load_data(input_path)
    df = update_outcome_timestamp(df)
    df = update_arrival_timestamp(df)
    df = clean_strings(df)
    df = rename_columns(df, RENAME_MAP)
    df = filter_emergency_room(df)
    df = drop_invalid_exams(df, REMOVE_VALUES)
    df = filter_columns(df, list(RENAME_MAP.values()))
    df = translate_test_department(
        df,
        TEST_DEPARTMENT_RENAMING_MAPPING
    )
    df = create_test_department_group(df, TEST_DEPARTMENT_GROUPING)
    df = convert_timestamps(df, TIMESTAMP_COLUMNS)
    df = add_synthetic_timestamps(df)
    df = map_outcome_values(df)
    df = map_triage_severity_values(df)
    df = dropna_by_column(df, column="triage_exit_severity")
    df = drop_invalid_timestamps(df)
    df = drop_2024_records(df, TIMESTAMP_COLUMNS)
    save_data(df, output_path)


if __name__ == "__main__":
    process_data(INPUT_CSV, OUTPUT_CSV)
