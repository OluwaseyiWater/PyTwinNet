from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Tuple, Any
import random
from ..core.digital_twin import DigitalTwin
from ..optimization.objective import Objective

Bounds2D = Tuple[Tuple[float,float], Tuple[float,float]]  # ((x_min,x_max),(y_min,y_max))

@dataclass
class PlacementGridOptimizer:
    """
    Grid search over positions for a set of nodes (e.g., gNBs).
    Beware combinatorics: keep grids small or optimize one node at a time.
    """
    grid_x: Iterable[float]
    grid_y: Iterable[float]
    fixed_z: float = 10.0
    copy_twin: bool = True

    def optimize(self, twin: DigitalTwin, objective: Objective, node_ids: List[str]) -> Dict[str, Any]:
        best_score = float("-inf")
        best_coords: Dict[str, Tuple[float,float,float]] = {}
        points = [(x,y,self.fixed_z) for x in self.grid_x for y in self.grid_y]
        combos = list(product(points, repeat=len(node_ids)))
        evals = 0
        for combo in combos:
            sim = twin.snapshot() if self.copy_twin else twin
            for nid, pos in zip(node_ids, combo):
                n = sim.network.get_node_by_id(nid)
                if n: n.move_to(pos)
            score = objective.evaluate(sim)
            evals += 1
            if score > best_score:
                best_score = score
                best_coords = {nid: pos for nid, pos in zip(node_ids, combo)}
        return {"best_score": best_score, "best_positions": best_coords, "evaluations": evals}

@dataclass
class PlacementRandomSearchOptimizer:
    """
    Randomly sample positions within bounds for given nodes.
    """
    bounds: Bounds2D
    samples: int = 200
    fixed_z: float = 10.0
    seed: int = 0
    copy_twin: bool = True

    def optimize(self, twin: DigitalTwin, objective: Objective, node_ids: List[str]) -> Dict[str, Any]:
        rng = random.Random(self.seed)
        (x0,x1),(y0,y1) = self.bounds
        best_score = float("-inf")
        best_coords: Dict[str, Tuple[float,float,float]] = {}
        for _ in range(self.samples):
            sim = twin.snapshot() if self.copy_twin else twin
            cur_coords = {}
            for nid in node_ids:
                x = rng.uniform(x0, x1); y = rng.uniform(y0, y1); z = self.fixed_z
                n = sim.network.get_node_by_id(nid)
                if n: n.move_to((x,y,z))
                cur_coords[nid] = (x,y,z)
            score = objective.evaluate(sim)
            if score > best_score:
                best_score = score
                best_coords = cur_coords
        return {"best_score": best_score, "best_positions": best_coords, "evaluations": self.samples}
