
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .events import Event

@dataclass
class Scenario:
    duration_s: float
    events: List[Event] = field(default_factory=list)
    def add_event(self, event: Event) -> None:
        self.events.append(event)
    def sorted_events(self) -> List[Event]:
        return sorted(self.events, key=lambda e: e.timestamp)
