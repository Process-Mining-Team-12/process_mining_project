import pandas as pd


# Minimal configuration — edit these values and run the script
INPUT_CSV = "data/raw/source_data.csv"  # path to source CSV
OUTPUT_CSV = "data/raw/filtered_data.csv"  # path to save filtered CSV
COLUMN = "DESCR_EROGATORE"  # column to check
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
df = pd.read_csv(INPUT_CSV)

# Find IDs that have at least one row with a value to remove in the target column
ids_to_remove = df.loc[df[COLUMN].isin(REMOVE_VALUES), "ID"].dropna().unique()
# Drop all rows whose ID is in that set
df = df[~df["ID"].isin(ids_to_remove)]

#PS keep only PS GENERALE
df = df[df["PS"] == "PS GENERALE"]

df.to_csv(OUTPUT_CSV, index=False)

