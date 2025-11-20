"""Data Processing Script"""
from datetime import timedelta
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
import math
import datetime as dt
import pandas as pd
import pm4py

INPUT_CSV = Path("data/raw/filtered_data.csv")


@dataclass
class BaseEvent(ABC):
    """Class representing the Event of a Log."""
    case_id: str
    name: str
    timestamp: dt.datetime

    def to_dict(self) -> dict[str, any]:
        """Return a flat dict ready to become a DataFrame row."""
        return {
            "case:concept:name": self.case_id,
            "concept:name": self.name,
            "time:timestamp": self.timestamp,
        }


@dataclass
class RegistrationEvent(BaseEvent):
    """Event REGISTRATION"""
    name: str = field(init=False, default="REGISTRATION")
    arrival_method: str
    # lifecycle_transition: str | None = None

    def to_dict(self):
        result = super().to_dict()
        result["arrival_method"] = self.arrival_method
        # if self.lifecycle_transition is not None:
        #     result["lifecycle:transition"] = self.lifecycle_transition
        return result


@dataclass
class StartTriageEntryEvent(BaseEvent):
    """Event START_TRIAGE_ENTRY"""
    name: str = field(init=False, default="START_TRIAGE_ENTRY")
    severity: str

    def to_dict(self):
        result = super().to_dict()
        result["triage_entry_severity"] = self.severity
        return result


@dataclass
class AcceptancyEvent(BaseEvent):
    """Event ACCEPTANCY"""
    name: str = field(init=False, default="ACCEPTANCY")


@dataclass
class TestInitialEvent(BaseEvent):
    """Event TEST INITIAL"""
    name: str = field(init=False, default="TEST_INITIAL")
    code: int
    description: str
    department: str
    lifecycle_transition: str | None = None

    def to_dict(self):
        result = super().to_dict()
        result["code"] = self.code
        result["description"] = self.description
        result["department"] = self.department
        if self.lifecycle_transition is not None:
            result["lifecycle:transition"] = self.lifecycle_transition
        return result

@dataclass
class TestFollowUpEvent(BaseEvent):
    """Event TEST FOLLOW UP"""
    name: str = field(init=False, default="TEST_FOLLOW_UP")
    code: int
    description: str
    department: str
    lifecycle_transition: str | None = None

    def to_dict(self):
        result = super().to_dict()
        result["code"] = self.code
        result["description"] = self.description
        result["department"] = self.department
        if self.lifecycle_transition is not None:
            result["lifecycle:transition"] = self.lifecycle_transition
        return result

@dataclass
class RequestVisitEvent(BaseEvent):
    """Event REQUEST_VISIT"""
    # No default value for name because it depends on the group
    name: str
    code: int
    description: str
    department: str

    def to_dict(self):
        result = super().to_dict()
        result["code"] = self.code
        result["description"] = self.description
        result["department"] = self.department
        return result

@dataclass
class VisitEvent(BaseEvent):
    """Event VISIT"""
    # No default value for name because it depends on the group
    name: str
    code: int
    description: str
    department: str
    lifecycle_transition: str | None = None

    def to_dict(self):
        result = super().to_dict()
        result["code"] = self.code
        result["description"] = self.description
        result["department"] = self.department
        if self.lifecycle_transition is not None:
            result["lifecycle:transition"] = self.lifecycle_transition
        return result


@dataclass
class OutcomeEvent(BaseEvent):
    """Event OUTCOME"""
    # No default value for name because it depends on the group
    name: str


@dataclass
class StartTriageExitEvent(BaseEvent):
    """Event START_TRIAGE_EXIT"""
    name: str = field(init=False, default="START_TRIAGE_EXIT")
    severity: str

    def to_dict(self):
        result = super().to_dict()
        result["triage_exit_severity"] = self.severity
        return result


@dataclass
class DischargeEvent(BaseEvent):
    """Event DISCHARGE"""
    name: str = field(init=False, default="DISCHARGE_EVENT")
    diagnosis_description: str
    diagnosis_class: str
    diagnosis_code: int

    def to_dict(self):
        result = super().to_dict()
        result["diagnosis_description"] = self.diagnosis_description
        result["diagnosis_class"] = self.diagnosis_class
        result["diagnosis_code"] = self.diagnosis_code
        return result


@dataclass
class Case:
    """Class representing a Patient Case"""
    case_id: str
    events: list[BaseEvent] = field(default_factory=list)

    def _normalize_timestamp(self, ts):
        """Ensure timestamp is a Python datetime, not a string."""
        if isinstance(ts, dt.datetime):
            return ts
        return pd.to_datetime(ts).to_pydatetime()

    def add_event(self, event: BaseEvent):
        """Add an event to the case"""
        assert event.case_id == self.case_id, "case_id mismatch!"
        event.timestamp = self._normalize_timestamp(event.timestamp)
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp)

    def add_events(self, events: list[BaseEvent]):
        """Add a list of events to the case"""
        for e in events:
            self.add_event(e)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert all events in the case to a DataFrame."""
        rows = [e.to_dict() for e in self.events]
        return pd.DataFrame(rows)


@dataclass
class EventLog:
    """Class representing the whole Log"""
    cases: list[Case] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        """Flatten all cases into a single dataframe."""
        rows = [c.to_dataframe() for c in self.cases]
        return pd.concat(rows, ignore_index=True)

    def to_xes(self, filepath: str):
        """Export the log to XES using pm4py."""
        df = self.to_dataframe()

        # Replace NaN with pd.NA (so pm4py ignores missing values)
        df = df.convert_dtypes()

        df = pm4py.format_dataframe(
            df,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp"
        )

        # Drop pm4py internal columns
        df = df.loc[:, ~df.columns.str.startswith("@@")]

        pm4py.write_xes(df, filepath)


def load_data(filepath: Path) -> pd.DataFrame:
    """Load CSV data from the given path."""
    return pd.read_csv(filepath, low_memory=False)


def get_unique_from_df(df: pd.DataFrame, key: str, disable_assert: bool = False):
    """Return the unique value from the dataframe."""
    value = {e[key] for _, e in df.iterrows()}
    if not disable_assert:
        assert len(value) == 1, f"More than one {key}: {value}! DF: {df!r}"
    return value.pop()


if __name__ == "__main__":
    dataframe = load_data(INPUT_CSV)

    log = EventLog()
    cases = dataframe.groupby('case_id')
    for case_id, event_df in cases:
        case = Case(case_id, [])

        registration_ts = get_unique_from_df(event_df, "registration_ts")
        triage_entry_ts = get_unique_from_df(event_df, "triage_entry_ts")
        acceptancy_ts = get_unique_from_df(event_df, "acceptancy_ts")
        outcome_ts = get_unique_from_df(event_df, "outcome_ts")
        triage_exit_ts = get_unique_from_df(event_df, "triage_exit_ts")
        discharge_ts = get_unique_from_df(event_df, "discharge_ts")

        # registration_ts_complete = get_unique_from_df(
        #     event_df,
        #     "registration_ts_complete"
        # )

        triage_entry_severity = get_unique_from_df(
            event_df,
            "triage_entry_severity"
        )
        triage_exit_severity = get_unique_from_df(
            event_df,
            "triage_exit_severity"
        )

        assert registration_ts < triage_entry_ts, f"{case_id}: {registration_ts} >= {acceptancy_ts}"
        assert triage_entry_ts < acceptancy_ts, f"{case_id}: {triage_entry_ts} >= {acceptancy_ts}"
        assert acceptancy_ts < triage_exit_ts, f"{case_id}: {acceptancy_ts} >= {triage_exit_ts}"

        # REGISTRATION EVENT
        arrival_method = get_unique_from_df(event_df, "arrival_method")
        case.add_event(RegistrationEvent(case_id, registration_ts, arrival_method))
        # if registration_ts_complete == registration_ts:
        #     case.add_event(RegistrationEvent(case_id, registration_ts, arrival_method))
        # else:
        #     case.add_events([
        #         RegistrationEvent(case_id, registration_ts, arrival_method, "start"),
        #         RegistrationEvent(case_id, registration_ts_complete, arrival_method, "complete")
        #     ])

        # TRIAGE ENTRY EVENT
        triage_entry = StartTriageEntryEvent(case_id, triage_entry_ts, triage_entry_severity)
        case.add_event(triage_entry)

        # ACCEPTANCY EVENT
        acceptancy = AcceptancyEvent(case_id, acceptancy_ts)
        case.add_event(acceptancy)

        test_and_visits = event_df.groupby([
            # "test_planned_ts",
            "request_visit_ts",
            "visit_code",
            "test_department"
        ])
        
        first_test = True
        for index, tv_df in test_and_visits:
            request_visit_ts = get_unique_from_df(tv_df, "request_visit_ts")
            complete_ts = get_unique_from_df(tv_df, "test_planned_ts", disable_assert=True)
            start_ts = pd.to_datetime(complete_ts) - timedelta(minutes=int(get_unique_from_df(tv_df, "average_visit_time")))
            if start_ts <= pd.to_datetime(request_visit_ts):
                start_ts = pd.to_datetime(request_visit_ts) + timedelta(seconds=1)
            code = get_unique_from_df(tv_df, "visit_code")
            desc = ",".join([tv["visit_description"] for _, tv in tv_df.iterrows()])
            department = get_unique_from_df(tv_df, "test_department")

            if get_unique_from_df(tv_df, "test_department") == "TEST":
                if first_test:
                    #  TEST INITIAL EVENT
                    case.add_events([
                        TestInitialEvent(case_id, start_ts, code, desc, department, "start"),
                        TestInitialEvent(case_id, complete_ts, code, desc, department, "complete")
                    ])
                    first_test = False
                else:
                    #  TEST FOLLOW UP EVENT
                    case.add_events([
                        TestFollowUpEvent(case_id, start_ts, code, desc, department, "start"),
                        TestFollowUpEvent(case_id, complete_ts, code, desc, department, "complete")
                    ])
            else:
                name = f"VISIT_{get_unique_from_df(tv_df, 'test_department_group')}"
                request_name = f"REQUEST_{name}"
                case.add_event(RequestVisitEvent(case_id, request_name, request_visit_ts, code, desc, department))
                case.add_events([
                    VisitEvent(case_id, name, start_ts, code, desc, department, "start"),
                    VisitEvent(case_id, name, complete_ts, code, desc, department, "complete")
                ])

        # OUCOME EVENT
        outcome_value = get_unique_from_df(event_df, "outcome_raw")
        outcome = OutcomeEvent(
            case_id,
            name=f"OUTCOME_{outcome_value}",
            timestamp=outcome_ts
        )
        case.add_event(outcome)

        # TRIAGE EXIT EVENT
        triage_exit = StartTriageExitEvent(
            case_id,
            timestamp=triage_exit_ts,
            severity=get_unique_from_df(event_df, "triage_exit_severity")
        )
        case.add_event(triage_exit)

        ddcs = {e["discharge_diagnosis_code"] for _, e in event_df.iterrows()}
        ddc = ddcs.pop()
        diagnosis_code = int(ddc) if not math.isnan(ddc) else -1
        # DISCHARGE EVENT
        discharge = DischargeEvent(
            case_id,
            diagnosis_description=get_unique_from_df(
                event_df,
                "discharge_diagnosis_description"
            ),
            diagnosis_class=get_unique_from_df(
                event_df,
                "discharge_diagnosis_class"
            ),
            diagnosis_code=int(diagnosis_code),
            timestamp=discharge_ts
        )
        case.add_event(discharge)

        log.cases.append(case)

    log.to_xes("output/log.xes")
