
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import random
@dataclass
class PoissonTraffic:
    rate_lambda: float
    seed: int = 0
    def arrivals(self, duration_s: float) -> List[float]:
        rng = random.Random(self.seed)
        t = 0.0; times = []
        while t <= duration_s:
            dt = rng.expovariate(self.rate_lambda) if self.rate_lambda > 0 else duration_s + 1
            t += dt
            if t <= duration_s:
                times.append(t)
        return times
