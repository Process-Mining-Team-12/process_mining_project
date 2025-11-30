"""Helper Functions"""
import math
import pandas as pd
from pathlib import Path

def load_data(filepath: Path) -> pd.DataFrame:
    """Load CSV data from the given path."""
    return pd.read_csv(filepath, low_memory=False)


def get_unique_from_df(df: pd.DataFrame, key: str, disable_assert: bool = False):
    """Return the unique value from the dataframe."""
    value = {e[key] for _, e in df.iterrows()}
    if not disable_assert:
        assert len(value) == 1, f"More than one {key}: {value}! DF: {df!r}"
    return value.pop()


def get_diagnosis_code(event_df: pd.DataFrame) -> int:
    """Extract and validate diagnosis code, handling NaN."""
    ddcs = {e["discharge_diagnosis_code"] for _, e in event_df.iterrows()}
    ddc = ddcs.pop()
    return int(ddc) if not math.isnan(ddc) else -1