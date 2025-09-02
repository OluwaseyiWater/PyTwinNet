from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List, Any, Iterable
from concurrent.futures import ProcessPoolExecutor, as_completed
import itertools
import math

from ..core.digital_twin import DigitalTwin
from .objective import Objective

Pos = Tuple[float, float, float]

def _eval_combo(snapshot: DigitalTwin, node_ids: List[str], coords: List[Pos], objective: Objective) -> Tuple[float, Dict[str, Pos]]:
    sim = snapshot  # already deep-copied by caller
    for nid, pos in zip(node_ids, coords):
        n = sim.network.get_node_by_id(nid)
        if n: n.move_to(pos)
    score = objective.evaluate(sim)
    return score, {nid: pos for nid, pos in zip(node_ids, coords)}

@dataclass
class ParallelPlacementGrid:
    grid_x: Iterable[float]
    grid_y: Iterable[float]
    fixed_z: float = 10.0
    max_workers: int = 0  # 0 -> use os.cpu_count()

    def optimize(self, twin: DigitalTwin, objective: Objective, node_ids: List[str]) -> Dict[str, Any]:
        points = [(x, y, self.fixed_z) for x, y in itertools.product(self.grid_x, self.grid_y)]
        combos = itertools.product(points, repeat=len(node_ids))
        best_score = -math.inf
        best_pos: Dict[str, Pos] = {}
        futures = []
        with ProcessPoolExecutor(max_workers=self.max_workers or None) as ex:
            for combo in combos:
                # Snapshot per job (so workers don't share state)
                snap = twin.snapshot()
                futures.append(ex.submit(_eval_combo, snap, node_ids, list(combo), objective))
            for fut in as_completed(futures):
                score, pos = fut.result()
                if score > best_score:
                    best_score, best_pos = score, pos
        return {"best_score": best_score, "best_positions": best_pos, "evaluations": len(futures)}
