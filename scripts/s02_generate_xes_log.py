"""Data Processing Script"""
from abc import ABC
from dataclasses import dataclass, field
import datetime as dt
import pandas as pd
import pm4py


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
        result['severity'] = self.severity
        return result


@dataclass
class Case:
    """Class representing a Patient Case"""
    case_id: str
    events: list[BaseEvent] = field(default_factory=list)

    def add_event(self, event: BaseEvent):
        """Add an event to the case"""
        assert event.case_id == self.case_id, 'case_id mismatch!'
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
        df = pm4py.format_dataframe(
            df,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp"
        )
        pm4py.write_xes(df, filepath)
