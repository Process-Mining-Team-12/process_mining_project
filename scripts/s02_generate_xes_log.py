"""Data Processing Script"""
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
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
class ArrivalEvent(BaseEvent):
    """Event ARRIVAL"""
    name: str = field(init=False, default="ARRIVAL")


@dataclass
class TriageEntryEvent(BaseEvent):
    """Event TRIAGE_ENTRY"""
    name: str = field(init=False, default="TRIAGE_ENTRY")
    severity: str

    def to_dict(self):
        result = super().to_dict()
        result["severity"] = self.severity
        return result


@dataclass
class Case:
    """Class representing a Patient Case"""
    case_id: str
    events: list[BaseEvent] = field(default_factory=list)

    def add_event(self, event: BaseEvent):
        """Add an event to the case"""
        assert event.case_id == self.case_id, "case_id mismatch!"
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp)

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

        # Replace NaN with None (so pm4py ignores missing values)
        df = df.where(pd.notnull(df), None)

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


def get_unique_from_df(df: pd.DataFrame, key: str):
    """Return the unique value from the dataframe."""
    value = {e[key] for _, e in df.iterrows()}
    assert len(value) == 1, f"More than one {key}!"
    return value.pop()


if __name__ == "__main__":
    dataframe = load_data(INPUT_CSV)

    log = EventLog()
    cases = dataframe.groupby('case_id')
    for case_id, event_df in cases:
        case = Case(case_id, [])

        arrival_ts = get_unique_from_df(event_df, "arrival_ts")
        triage_entry_ts = get_unique_from_df(event_df, "triage_entry_ts")
        acceptancy_ts = get_unique_from_df(event_df, "acceptancy_ts")
        triage_exit_ts = get_unique_from_df(event_df, "triage_exit_ts")

        triage_entry_severity = get_unique_from_df(
            event_df,
            "triage_entry_severity"
        )
        triage_exit_severity = get_unique_from_df(
            event_df,
            "triage_exit_severity"
        )

        assert arrival_ts < triage_entry_ts
        assert triage_entry_ts < acceptancy_ts
        assert acceptancy_ts < triage_exit_ts

        arrival = ArrivalEvent(case_id, arrival_ts)
        case.add_event(arrival)

        triage_entry = TriageEntryEvent(
            case_id,
            triage_entry_ts,
            triage_entry_severity
        )
        case.add_event(triage_entry)

        # for index, event in event_df.iterrows():
        #     pass

        log.cases.append(case)

    log.to_xes("output/log.xes")
