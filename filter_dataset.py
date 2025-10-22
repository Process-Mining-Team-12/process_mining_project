import pandas as pd


# Minimal configuration — edit these values and run the script
INPUT_CSV = "merged_pratiche_ps_2023.csv"  # path to source CSV
OUTPUT_CSV = "data/dataset_filtered.csv"  # path to save filtered CSV
COLUMN = "DESCR_EROGATORE"  # column to check
REMOVE_VALUES = [
	"Eliot",
	# "ER ROOM 2",
]
df = pd.read_csv(INPUT_CSV)

# Find IDs that have at least one row with a value to remove in the target column
ids_to_remove = df.loc[df[COLUMN].isin(REMOVE_VALUES), "ID"].dropna().unique()
# Drop all rows whose ID is in that set
df = df[~df["ID"].isin(ids_to_remove)]

#PS keep only PS GENERALE
df = df[df["PS"] == "PS GENERALE"]

df.to_csv(OUTPUT_CSV, index=False)

