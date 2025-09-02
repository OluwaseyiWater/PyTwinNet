
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Environment:
    dimensions_m: Tuple[float, float, float] = (100.0, 100.0, 30.0)
    obstacles: List[object] = field(default_factory=list)
    def is_within_bounds(self, position: Tuple[float, float, float]) -> bool:
        x, y, z = position
        w, d, h = self.dimensions_m
        return 0.0 <= x <= w and 0.0 <= y <= d and 0.0 <= z <= h
