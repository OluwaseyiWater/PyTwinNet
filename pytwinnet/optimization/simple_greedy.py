
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Tuple, List
from ..core.digital_twin import DigitalTwin
from ..core.node import WirelessNode
from .objective import Objective
from .optimizer import Optimizer

@dataclass
class SimpleGreedyOptimizer(Optimizer):
    step_db: float = 1.0
    max_power_dbm: float = 30.0
    iterations: int = 10
    def optimize(self, twin: DigitalTwin, objective: Objective) -> Dict[str, Any]:
        best_score = objective.evaluate(twin)
        history: List[Tuple[str, float]] = []
        for _ in range(self.iterations):
            candidates = list(twin.network)
            if not candidates: break
            def proxy(n: WirelessNode) -> float:
                return float(n.metadata.get("received_traffic_mbps", 0.0))
            worst = min(candidates, key=proxy)
            props = worst.transceiver_properties
            new_pw = min(props.transmit_power_dbm + self.step_db, self.max_power_dbm)
            props.transmit_power_dbm = new_pw
            score = objective.evaluate(twin)
            history.append((worst.node_id, score))
            if score > best_score:
                best_score = score
        return {"best_score": best_score, "iterations": len(history), "metadata": {"history": history}}
