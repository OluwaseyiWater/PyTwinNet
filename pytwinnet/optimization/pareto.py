from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Any, List, Tuple

@dataclass
class MultiObjectiveSampler:
    """Sample candidates, evaluate 2 objectives, and return Pareto set (maximize both)."""
    sampler: Callable[[], Dict[str, Any]]
    evaluate: Callable[[Dict[str, Any]], Tuple[float, float]]
    samples: int = 200

    def run(self) -> Dict[str, Any]:
        pts: List[Dict[str, Any]] = []
        vals: List[Tuple[float, float]] = []
        for _ in range(self.samples):
            x = self.sampler()
            v = self.evaluate(x)
            pts.append(x); vals.append(v)
        pareto = []
        for i, v in enumerate(vals):
            dominated = False
            for j, u in enumerate(vals):
                if j == i: continue
                if u[0] >= v[0] and u[1] >= v[1] and (u[0] > v[0] or u[1] > v[1]):
                    dominated = True; break
            if not dominated:
                pareto.append((pts[i], v))
        return {"pareto": pareto, "all": list(zip(pts, vals))}
