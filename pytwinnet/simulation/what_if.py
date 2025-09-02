
from __future__ import annotations
from typing import Dict, Any
from .simulator import Simulator
from .scenario import Scenario
from ..core.digital_twin import DigitalTwin
from ..optimization.objective import Objective

def what_if(twin: DigitalTwin, scenario: Scenario, objective: Objective | None = None) -> Dict[str, Any]:
    sim = Simulator(twin)
    out = sim.run(scenario, copy_twin=True)
    score = objective.evaluate(out) if objective is not None else None
    return {"twin": out, "score": score}
