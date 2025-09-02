
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, Any, List, Tuple
from ..core.digital_twin import DigitalTwin
from .objective import Objective
from .optimizer import Optimizer

@dataclass
class GridSearchOptimizer(Optimizer):
    param_grid: Dict[str, Iterable[float]]
    copy_twin: bool = True
    def optimize(self, twin: DigitalTwin, objective: Objective) -> Dict[str, Any]:
        node_ids = list(self.param_grid.keys())
        candidates = list(product(*[list(self.param_grid[n]) for n in node_ids]))
        best_score = float("-inf")
        best_combo: List[Tuple[str, float]] = []
        for combo in candidates:
            sim_twin = twin.snapshot() if self.copy_twin else twin
            for nid, pw in zip(node_ids, combo):
                node = sim_twin.network.get_node_by_id(nid)
                if node:
                    node.transceiver_properties.transmit_power_dbm = float(pw)
            score = objective.evaluate(sim_twin)
            if score > best_score:
                best_score = score
                best_combo = list(zip(node_ids, map(float, combo)))
        return {"best_score": best_score, "best_params": best_combo, "evaluations": len(candidates)}
