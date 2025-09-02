
from __future__ import annotations
from dataclasses import dataclass
from ..core.digital_twin import DigitalTwin
from .scenario import Scenario

@dataclass
class Simulator:
    twin: DigitalTwin
    def run(self, scenario: Scenario, copy_twin: bool = True) -> DigitalTwin:
        sim_twin = self.twin.snapshot() if copy_twin else self.twin
        for event in scenario.sorted_events():
            if 0.0 <= event.timestamp <= scenario.duration_s:
                event.apply(sim_twin)
        return sim_twin
