
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Any, List
import random
from ..core.digital_twin import DigitalTwin
from .objective import Objective
from .optimizer import Optimizer

@dataclass
class RandomSearchOptimizer(Optimizer):
    ranges_dbm: Dict[str, Tuple[float, float]]
    samples: int = 32
    seed: int = 0
    copy_twin: bool = True
    def optimize(self, twin: DigitalTwin, objective: Objective) -> Dict[str, Any]:
        rng = random.Random(self.seed)
        node_ids = list(self.ranges_dbm.keys())
        best_score = float("-inf")
        best_params: List[Tuple[str, float]] = []
        for _ in range(self.samples):
            sim_twin = twin.snapshot() if self.copy_twin else twin
            draw = []
            for nid in node_ids:
                mn, mx = self.ranges_dbm[nid]
                val = rng.uniform(float(mn), float(mx))
                node = sim_twin.network.get_node_by_id(nid)
                if node:
                    node.transceiver_properties.transmit_power_dbm = float(val)
                draw.append((nid, float(val)))
            score = objective.evaluate(sim_twin)
            if score > best_score:
                best_score = score
                best_params = draw
        return {"best_score": best_score, "best_params": best_params, "evaluations": self.samples}
