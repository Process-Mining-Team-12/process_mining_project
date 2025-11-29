"""Domain Models (Events & Structures)"""
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
class RegistrationEvent(BaseEvent):
    """Event REGISTRATION"""
    name: str = field(init=False, default="REGISTRATION")
    arrival_method: str

    def to_dict(self):
        result = super().to_dict()
        result["arrival_method"] = self.arrival_method
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
        df = df.convert_dtypes() # Replace NaN with pd.NA
        
        df = pm4py.format_dataframe(
            df,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp"
        )
        
        # Drop pm4py internal columns
        df = df.loc[:, ~df.columns.str.startswith("@@")]
        pm4py.write_xes(df, filepath)