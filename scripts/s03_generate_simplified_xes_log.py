"""Data Processing Script that generates a log to be compared with Italian Waiting Time guidelines"""

from pathlib import Path
import pandas as pd
from domain import *
from helpers import *


INPUT_CSV = Path("data/raw/filtered_data.csv")
OUTPUT_XES = Path("output/log_simplified.xes")


def process_case(case_id: str, event_df: pd.DataFrame) -> Case:
    """Processes a single patient case and returns the populated Case object."""
    case = Case(case_id, [])

    timestamps = {
        "triage_in": get_unique_from_df(event_df, "triage_entry_ts"),
        "accept": get_unique_from_df(event_df, "acceptancy_ts"),
    }

    assert timestamps["triage_in"] < timestamps["accept"], f"{case_id}: {timestamps['triage_in']} >= {timestamps['accept']}"

    # 1. Triage Entry Event
    triage_entry_severity = get_unique_from_df(event_df, "triage_entry_severity")
    case.add_event(StartTriageEntryEvent(case_id, timestamps["triage_in"], triage_entry_severity))

    # 2. Acceptancy Event
    case.add_event(AcceptancyEvent(case_id, timestamps["accept"]))

    return case


if __name__ == "__main__":
    dataframe = load_data(INPUT_CSV)
    log = EventLog()
    
    grouped_cases = dataframe.groupby('case_id')
    
    for case_id, event_df in grouped_cases:
        case = process_case(str(case_id), event_df)
        log.cases.append(case)

    log.to_xes(str(OUTPUT_XES))