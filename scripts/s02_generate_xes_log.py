"""Data Processing Script"""
from datetime import timedelta
from pathlib import Path
import pandas as pd
from domain import *
from helpers import *


INPUT_CSV = Path("data/raw/filtered_data.csv")
OUTPUT_XES = Path("output/log.xes")


def process_tests_and_visits(case: Case, event_df: pd.DataFrame):
    """Processes clinical tests and visit events grouping."""
    test_and_visits = event_df.groupby([
        "request_visit_ts",
        "visit_code",
        "test_department"
    ])
    
    first_test = True
    
    for _, tv_df in test_and_visits:
        # Extract metadata
        request_visit_ts = get_unique_from_df(tv_df, "request_visit_ts")
        complete_ts = get_unique_from_df(tv_df, "test_planned_ts", disable_assert=True)
        avg_time = int(get_unique_from_df(tv_df, "average_visit_time"))
        code = get_unique_from_df(tv_df, "visit_code")
        department = get_unique_from_df(tv_df, "test_department")
        desc = ",".join([tv["visit_description"] for _, tv in tv_df.iterrows()])

        # Calculate Start Timestamp
        start_ts = pd.to_datetime(complete_ts) - timedelta(minutes=avg_time)
        request_ts_dt = pd.to_datetime(request_visit_ts)
        
        if start_ts <= request_ts_dt:
            start_ts = request_ts_dt + timedelta(seconds=1)

        # Logic Branch: Test vs Visit
        if department == "TEST":
            EventClass = TestInitialEvent if first_test else TestFollowUpEvent
            case.add_events([
                EventClass(case.case_id, start_ts, code, desc, department, "start"),
                EventClass(case.case_id, complete_ts, code, desc, department, "complete")
            ])
            first_test = False
        else:
            group_name = get_unique_from_df(tv_df, 'test_department_group')
            name = f"VISIT_{group_name}"
            request_name = f"REQUEST_{name}"
            
            case.add_event(RequestVisitEvent(case.case_id, request_name, request_visit_ts, code, desc, department))
            case.add_events([
                VisitEvent(case.case_id, name, start_ts, code, desc, department, "start"),
                VisitEvent(case.case_id, name, complete_ts, code, desc, department, "complete")
            ])


def process_case(case_id: str, event_df: pd.DataFrame) -> Case:
    """Processes a single patient case and returns the populated Case object."""
    case = Case(case_id, [])

    timestamps = {
        "reg": get_unique_from_df(event_df, "registration_ts"),
        "triage_in": get_unique_from_df(event_df, "triage_entry_ts"),
        "accept": get_unique_from_df(event_df, "acceptancy_ts"),
        "triage_out": get_unique_from_df(event_df, "triage_exit_ts"),
        "outcome": get_unique_from_df(event_df, "outcome_ts"),
        "discharge": get_unique_from_df(event_df, "discharge_ts"),
    }

    assert timestamps["reg"] < timestamps["triage_in"], f"{case_id}: {timestamps['reg']} >= {timestamps['accept']}"
    assert timestamps["triage_in"] < timestamps["accept"], f"{case_id}: {timestamps['triage_in']} >= {timestamps['accept']}"
    assert timestamps["accept"] < timestamps["triage_out"], f"{case_id}: {timestamps['accept']} >= {timestamps['triage_out']}"

    # 1. Registration Event
    arrival_method = get_unique_from_df(event_df, "arrival_method")
    case.add_event(RegistrationEvent(case_id, timestamps["reg"], arrival_method))

    # 2. Triage Entry Event
    triage_entry_severity = get_unique_from_df(event_df, "triage_entry_severity")
    case.add_event(StartTriageEntryEvent(case_id, timestamps["triage_in"], triage_entry_severity))

    # 3. Acceptancy Event
    case.add_event(AcceptancyEvent(case_id, timestamps["accept"]))

    # 4. Clinical Activities (Tests & Visits)
    process_tests_and_visits(case, event_df)

    # 5. Outcome Event
    outcome_val = get_unique_from_df(event_df, "outcome_raw")
    case.add_event(OutcomeEvent(case_id, f"OUTCOME_{outcome_val}", timestamps["outcome"]))

    # 6. Triage Exit Event
    triage_exit_severity = get_unique_from_df(event_df, "triage_exit_severity")
    case.add_event(StartTriageExitEvent(case_id, timestamps["triage_out"], triage_exit_severity))

    # 7. Discharge Event
    diagnosis_code = get_diagnosis_code(event_df)
    case.add_event(DischargeEvent(
        case_id,
        diagnosis_description=get_unique_from_df(event_df, "discharge_diagnosis_description"),
        diagnosis_class=get_unique_from_df(event_df, "discharge_diagnosis_class"),
        diagnosis_code=diagnosis_code,
        timestamp=timestamps["discharge"]
    ))

    return case


if __name__ == "__main__":
    dataframe = load_data(INPUT_CSV)
    log = EventLog()
    
    grouped_cases = dataframe.groupby('case_id')
    
    for case_id, event_df in grouped_cases:
        case = process_case(str(case_id), event_df)
        log.cases.append(case)

    log.to_xes(str(OUTPUT_XES))